import sqlite3
import csv
import os
import re
from collections import defaultdict


def sanitize_name(name):
    """
    Convert arbitrary column/table names into SQLite-safe identifiers.
    """
    name = name.strip().lower()
    name = re.sub(r'\W+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')


def infer_relationship_groups(columns):
    """
    Detect logical entity groups from column prefixes.

    Example:
        supplier_name, supplier_phone -> supplier entity
        customer_id, customer_email -> customer entity

    Returns:
        {
            "supplier": ["supplier_name", "supplier_phone"],
            "customer": ["customer_id", "customer_email"]
        }
    """
    groups = defaultdict(list)

    for col in columns:
        parts = col.split('_')

        if len(parts) >= 2:
            prefix = parts[0]

            # Ignore common generic prefixes
            if prefix not in {"id"}:
                groups[prefix].append(col)

    # Keep only groups with 2+ related columns
    return {
        group: cols
        for group, cols in groups.items()
        if len(cols) >= 2
    }


def create_lookup_table(cursor, staging_table, group_name, columns):
    """
    Create a normalized lookup table dynamically.
    """
    table_name = sanitize_name(group_name)

    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

    # Build schema dynamically
    schema_cols = []

    for col in columns:
        attr = col[len(group_name) + 1:]  # remove prefix_
        attr = sanitize_name(attr)

        if attr == "id":
            schema_cols.append(f'"{attr}" TEXT UNIQUE')
        else:
            schema_cols.append(f'"{attr}" TEXT')

    schema_sql = ", ".join(schema_cols)

    cursor.execute(f'''
        CREATE TABLE "{table_name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {schema_sql}
        )
    ''')

    # Insert unique combinations
    select_cols = ", ".join([f'"{c}"' for c in columns])

    target_cols = []
    for col in columns:
        attr = col[len(group_name) + 1:]
        target_cols.append(f'"{sanitize_name(attr)}"')

    target_sql = ", ".join(target_cols)

    cursor.execute(f'''
        INSERT INTO "{table_name}" ({target_sql})
        SELECT DISTINCT {select_cols}
        FROM "{staging_table}"
    ''')


def detect_primary_column(columns):
    """
    Try to detect a likely primary identifier column.
    """
    priority = [
        "id",
        "uuid",
        "serial",
        "serial_number",
        "email",
        "name"
    ]

    lowered = [c.lower() for c in columns]

    for candidate in priority:
        for original in columns:
            if candidate == original.lower():
                return original

    return None


def transform_csv_to_relational(csv_path, db_path=None):
    """
    Transform ANY CSV file into a normalized SQLite relational database.

    Features:
    - Automatic delimiter detection
    - Dynamic schema creation
    - Entity/lookup table inference
    - Foreign key generation
    - Handles arbitrary CSV structures
    """

    if db_path is None:
        base = os.path.splitext(os.path.basename(csv_path))[0]
        db_path = f"{base}.db"

    # ------------------------------------------------------------
    # 1. Read CSV
    # ------------------------------------------------------------
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:

        sample = f.read(4096)
        f.seek(0)

        dialect = csv.Sniffer().sniff(sample)
        reader = csv.DictReader(f, dialect=dialect)

        rows = list(reader)

        if not reader.fieldnames:
            raise ValueError("CSV file has no header row.")

        original_columns = reader.fieldnames

    columns = [sanitize_name(c) for c in original_columns]

    print(f"Detected columns:")
    for c in columns:
        print(f"  - {c}")

    # ------------------------------------------------------------
    # 2. Connect DB
    # ------------------------------------------------------------
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    # ------------------------------------------------------------
    # 3. Create staging table
    # ------------------------------------------------------------
    staging_table = "staging"

    cursor.execute(f'DROP TABLE IF EXISTS "{staging_table}"')

    schema = ", ".join([f'"{c}" TEXT' for c in columns])

    cursor.execute(f'''
        CREATE TABLE "{staging_table}" (
            {schema}
        )
    ''')

    placeholders = ", ".join(["?"] * len(columns))

    insert_sql = f'''
        INSERT INTO "{staging_table}"
        VALUES ({placeholders})
    '''

    for row in rows:
        values = [row[orig] for orig in original_columns]
        cursor.execute(insert_sql, values)

    conn.commit()

    print(f"\nImported {len(rows)} rows into staging table.")

    # ------------------------------------------------------------
    # 4. Infer lookup/entity tables
    # ------------------------------------------------------------
    relationship_groups = infer_relationship_groups(columns)

    print("\nDetected entity groups:")

    for group, cols in relationship_groups.items():
        print(f"  - {group}: {cols}")

    # Create lookup tables
    for group, cols in relationship_groups.items():
        create_lookup_table(
            cursor,
            staging_table,
            group,
            cols
        )

    conn.commit()

    # ------------------------------------------------------------
    # 5. Create main fact table
    # ------------------------------------------------------------
    main_table = "main_records"

    cursor.execute(f'DROP TABLE IF EXISTS "{main_table}"')

    lookup_columns = set()

    for cols in relationship_groups.values():
        lookup_columns.update(cols)

    fact_columns = [
        c for c in columns
        if c not in lookup_columns
    ]

    fact_schema = []

    primary_col = detect_primary_column(fact_columns)

    for col in fact_columns:

        if col == primary_col:
            fact_schema.append(f'"{col}" TEXT UNIQUE')
        else:
            fact_schema.append(f'"{col}" TEXT')

    # Add foreign keys
    fk_defs = []

    for group in relationship_groups.keys():

        fk_col = f"{group}_id"

        fact_schema.append(f'"{fk_col}" INTEGER')

        fk_defs.append(
            f'FOREIGN KEY("{fk_col}") REFERENCES "{group}"(id)'
        )

    schema_sql = ", ".join(fact_schema + fk_defs)

    cursor.execute(f'''
        CREATE TABLE "{main_table}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {schema_sql}
        )
    ''')

    # ------------------------------------------------------------
    # 6. Populate main table
    # ------------------------------------------------------------
    select_parts = []
    join_parts = []

    # Fact columns
    for col in fact_columns:
        select_parts.append(f's."{col}"')

    # Foreign key mappings
    for group, cols in relationship_groups.items():

        alias = group[0:3]

        select_parts.append(f'{alias}.id')

        join_conditions = []

        for col in cols:

            attr = col[len(group) + 1:]
            attr = sanitize_name(attr)

            join_conditions.append(
                f's."{col}" = {alias}."{attr}"'
            )

        join_sql = " AND ".join(join_conditions)

        join_parts.append(
            f'LEFT JOIN "{group}" {alias} ON {join_sql}'
        )

    insert_cols = fact_columns + [
        f"{group}_id"
        for group in relationship_groups.keys()
    ]

    insert_sql = ", ".join([f'"{c}"' for c in insert_cols])

    select_sql = ", ".join(select_parts)

    joins_sql = "\n".join(join_parts)

    cursor.execute(f'''
        INSERT INTO "{main_table}" ({insert_sql})
        SELECT {select_sql}
        FROM "{staging_table}" s
        {joins_sql}
    ''')

    conn.commit()

    # ------------------------------------------------------------
    # 7. Summary
    # ------------------------------------------------------------
    print("\nNormalization complete.")

    cursor.execute(f'SELECT COUNT(*) FROM "{main_table}"')
    total = cursor.fetchone()[0]

    print(f"Main records: {total}")

    for group in relationship_groups.keys():

        cursor.execute(f'SELECT COUNT(*) FROM "{group}"')

        count = cursor.fetchone()[0]

        print(f"{group}: {count} unique rows")

    # ------------------------------------------------------------
    # 8. Sample query
    # ------------------------------------------------------------
    cursor.execute(f'''
        SELECT *
        FROM "{main_table}"
        LIMIT 5
    ''')

    print("\nSample rows:")

    for row in cursor.fetchall():
        print(row)

    # ------------------------------------------------------------
    # 9. Cleanup
    # ------------------------------------------------------------
    cursor.execute(f'DROP TABLE "{staging_table}"')

    conn.commit()
    conn.close()

    print(f"\nSQLite database saved to: {db_path}")

if __name__ == '__main__':

    import sys

    print("Starting CSV -> SQLite conversion...")

    # --------------------------------------------------------
    # Validate arguments
    # --------------------------------------------------------
    if len(sys.argv) < 2:

        print("\nUsage:")
        print("python script.py <input_csv> [output_db]")
        print("\nExample:")
        print("python script.py data.csv output.db")

        sys.exit(1)

    input_csv = sys.argv[1]

    # Optional output DB
    if len(sys.argv) >= 3:
        output_db = sys.argv[2]
    else:
        base = os.path.splitext(os.path.basename(input_csv))[0]
        output_db = f"{base}.db"

    # Ensure .db extension
    if not output_db.endswith(".db"):
        output_db += ".db"

    # --------------------------------------------------------
    # Check input file
    # --------------------------------------------------------
    print(f"\nInput CSV: {input_csv}")
    print(f"Output DB: {output_db}")

    if not os.path.exists(input_csv):

        print(f"\nERROR: CSV file not found:")
        print(input_csv)

        sys.exit(1)

    # --------------------------------------------------------
    # Run conversion
    # --------------------------------------------------------
    try:

        transform_csv_to_relational(
            csv_path=input_csv,
            db_path=output_db
        )

        print("\nSUCCESS")
        print(f"Database created: {output_db}")

    except Exception as e:

        print("\nERROR during conversion:")
        print(str(e))
