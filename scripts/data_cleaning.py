# ============================================================================
# Data Cleaning Script
# Description: Comprehensive data cleaning script that processes an "ugly" CSV
#              file and outputs a clean version.
# Usage: python data_cleaning.py path/to/ugly_file.csv
# ============================================================================

import pandas as pd
import numpy as np
import sys
import os
import re
from pathlib import Path

# ============================================================================
# INPUT: Get file path from command-line argument
# ============================================================================
if len(sys.argv) < 2:
    print("Error: Please provide the path to your CSV file as an argument.")
    print("Usage: python data_cleaning.py path/to/ugly_file.csv")
    sys.exit(1)

input_file = sys.argv[1]

# Check if file exists
if not os.path.exists(input_file):
    print(f"File not found: {input_file}")
    print("Please check the file path and try again.")
    sys.exit(1)

print(f"Processing file: {input_file}")

# ============================================================================
# Load data
# ============================================================================
print("\n--- Loading data ---")
df = pd.read_csv(input_file)

# ============================================================================
# Get basic overview of the data
# ============================================================================
print("\n--- Basic Data Overview ---")

# Check memory usage
memory_usage = df.memory_usage(deep=True).sum() / 1024**2
print(f"Memory usage: {memory_usage:.2f} MB")

# Get basic dataset overview
print(f"Dimensions: {df.shape[0]} x {df.shape[1]}")
print("\nColumn names:")
print(list(df.columns))

print("\nFirst few rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

# ============================================================================
# Step 1: Detect and convert fake NA entries
# ============================================================================
print("\n--- Step 1: Detecting and fixing fake NA entries ---")

# Pattern for different ways NAs are stored
na_pattern = r"^(na|nan|n/a|#n/a|#n/d|#rif!|null|none|missing|nil|unknown|blank|\.*|-+|/+|_+|\?+)?$"

# Find different representations of NA values
different_ways_nas = set()
for col in df.columns:
    for val in df[col].dropna().astype(str).unique():
        val_stripped = val.strip()
        if re.match(na_pattern, val_stripped, re.IGNORECASE):
            different_ways_nas.add(val)

if different_ways_nas:
    print("Found different representations of NA values:")
    print(different_ways_nas)

# Convert all fake NAs to proper NA values
def convert_fake_nas(df):
    for col in df.columns:
        # Convert to string, preserving NaN
        df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)
        # Replace fake NA strings with np.nan
        df[col] = df[col].replace(na_pattern, np.nan, regex=True)
    return df

df = convert_fake_nas(df)
print("Fake NA values have been converted to proper NA values.")

# ============================================================================
# Step 2: Fix errors in scoring (I/l/o/O misclassifications)
# ============================================================================
print("\n--- Step 2: Fixing character-number errors (I/l/o/O) ---")

def fix_character_errors(df):
    for col in df.columns:
        # Try to convert to string first, preserving NaN
        col_str = df[col].astype(str)
        
        # Replace I and l with 1, o and O with 0
        col_str = col_str.replace(['I', 'l'], '1', regex=False)
        col_str = col_str.replace(['o', 'O'], '0', regex=False)
        
        # Try to convert to numeric
        try:
            num_col = pd.to_numeric(col_str, errors='coerce')
            
            # Convert to numeric only if most values are numeric (> 80%)
            non_na_ratio = num_col.notna().sum() / len(num_col)
            if non_na_ratio > 0.8:
                df[col] = num_col
        except:
            pass
    
    return df

df = fix_character_errors(df)
print("Character-number errors have been fixed.")

# ============================================================================
# Step 3: Eliminate rows with invalid user_id
# ============================================================================
print("\n--- Step 3: Eliminating rows with invalid user_id ---")

initial_rows = len(df)

if "user_id" in df.columns:
    df = df[df['user_id'] != 0]
    df = df[df['user_id'] != ' ']
    df = df[df['user_id'].notna()]
    
    removed_rows = initial_rows - len(df)
    print(f"Removed {removed_rows} rows with invalid user_id.")

# ============================================================================
# Step 4: Identify and remove duplicated data
# ============================================================================
print("\n--- Step 4: Removing duplicate records ---")

if "user_id" in df.columns:
    dup_count = len(df) - len(df.drop_duplicates(subset=['user_id']))
    
    if dup_count > 0:
        print(f"Found {dup_count} duplicate records.")
        
        # Remove duplicates, keeping the first occurrence
        df = df.drop_duplicates(subset=['user_id'], keep='first')
        
        print("Duplicates removed.")
    else:
        print("No duplicates found.")

# ============================================================================
# Step 5: Correct corrupted categories
# ============================================================================
print("\n--- Step 5: Correcting corrupted categories ---")

if "country" in df.columns:
    # Show the distribution before correction
    print("\nCountry values before correction:")
    print(df['country'].value_counts())
    
    # Standardize country names
    df['country'] = df['country'].apply(lambda x: str(x).strip().lower() if pd.notna(x) else x)
    
    # Map all USA variants to "USA"
    usa_variants = ['usa', 'us', 'u.s.a', 'united states']
    df.loc[df['country'].isin(usa_variants), 'country'] = 'USA'
    
    # Capitalize properly
    df['country'] = df['country'].apply(lambda x: x.upper() if pd.notna(x) else x)
    
    print("\nCountry values after correction:")
    print(df['country'].value_counts())

# ============================================================================
# Final overview of cleaned data
# ============================================================================
print("\n--- Final Data Summary ---")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print("\nData types after cleaning:")
print(df.dtypes)

# ============================================================================
# OUTPUT: Save cleaned data to CSV
# ============================================================================
print("\n--- Saving cleaned data ---")

# Generate output filename
output_file = input_file.replace('.csv', '_CLEAN.csv')

# Write the cleaned dataframe to CSV
df.to_csv(output_file, index=False)

print(f"✓ Cleaned data saved to: {output_file}")
print("\n--- Data cleaning complete! ---")
