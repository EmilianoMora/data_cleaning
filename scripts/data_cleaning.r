# ============================================================================
# Data Cleaning Script
# Description: Comprehensive data cleaning script that processes an "ugly" CSV
#              file and outputs a clean version.
# Usage: Rscript data_cleaning_script.R path/to/ugly_file.csv
# ============================================================================

# Install and load required packages
packages <- c("tidyverse", "data.table", "lubridate", "stringr", "ggplot2", "janitor", "skimr", "corrplot")

for (pkg in packages) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg)
    library(pkg, character.only = TRUE)
  }
}

# ============================================================================
# INPUT: Get file path from command-line argument
# ============================================================================
args <- commandArgs(trailingOnly = TRUE)

if (length(args) == 0) {
  stop("Error: Please provide the path to your CSV file as an argument.\n",
       "Usage: Rscript data_cleaning_script.R path/to/ugly_file.csv")
}

input_file <- args[1]

# Check if file exists
if (!file.exists(input_file)) {
  stop("File not found: ", input_file, "\nPlease check the file path and try again.")
}

cat("Processing file:", input_file, "\n")

# ============================================================================
# Load data
# ============================================================================
cat("\n--- Loading data ---\n")
df <- read_csv(input_file, col_names = TRUE)

# ============================================================================
# Get basic overview of the data
# ============================================================================
cat("\n--- Basic Data Overview ---\n")

# Check memory usage
cat("Memory usage:", format(object.size(df), units = "MB"), "\n")

# Get basic dataset overview
cat("Dimensions:", paste(dim(df), collapse = " x "), "\n")
cat("\nColumn names:\n")
print(colnames(df))

cat("\nFirst few rows:\n")
print(head(df))

cat("\nData types:\n")
print(str(df))

# ============================================================================
# Step 1: Detect and convert fake NA entries
# ============================================================================
cat("\n--- Step 1: Detecting and fixing fake NA entries ---\n")

# Find different ways NAs are stored
different_ways_NAs <- unique(unlist(lapply(df, function(x) unique(x[grepl("^(na|nan|n/a|#n/a|#n/d|#RIF!|null|none|missing|nil|unknown|blank|\\.*|-+|/+|_+|\\?+)?$", trimws(as.character(x)), ignore.case = TRUE)]))))

if (length(different_ways_NAs) > 0) {
  cat("Found different representations of NA values:\n")
  print(different_ways_NAs)
}

# Convert all fake NAs to proper NA values
df[] <- lapply(df, function(x) {
  x <- trimws(as.character(x))
  x[grepl("^(na|nan|n/a|#n/a|#n/d|#RIF!|null|none|missing|nil|unknown|blank|\\.*|-+|/+|_+|\\?+)?$", x, ignore.case = TRUE)] <- NA
  x
})

cat("Fake NA values have been converted to proper NA values.\n")

# ============================================================================
# Step 2: Fix errors in scoring (I/l/o/O misclassifications)
# ============================================================================
cat("\n--- Step 2: Fixing character-number errors (I/l/o/O) ---\n")

df[] <- lapply(df, function(col) {
  
  # Replace I and l with 1, o and O with 0
  col[col %in% c("I", "l")] <- "1"
  col[col %in% c("o", "O")] <- "0"
  
  suppressWarnings({
    num_col <- as.numeric(col)
    
    # Convert to numeric only if most values are numeric (> 80%)
    if(mean(!is.na(num_col)) > 0.8) {
      return(num_col)
    }
  })
  
  return(col)
})

cat("Character-number errors have been fixed.\n")

# ============================================================================
# Step 3: Eliminate rows with invalid user_id
# ============================================================================
cat("\n--- Step 3: Eliminating rows with invalid user_id ---\n")

initial_rows <- nrow(df)

if ("user_id" %in% colnames(df)) {
  df <- filter(df, user_id != 0) %>%
    filter(user_id != " ")
  
  removed_rows <- initial_rows - nrow(df)
  cat("Removed", removed_rows, "rows with invalid user_id.\n")
}

# ============================================================================
# Step 4: Identify and remove duplicated data
# ============================================================================
cat("\n--- Step 4: Removing duplicate records ---\n")

if ("user_id" %in% colnames(df)) {
  # Find duplicated entries
  dup_count <- nrow(df) - nrow(distinct(df, user_id, .keep_all = TRUE))
  
  if (dup_count > 0) {
    cat("Found", dup_count, "duplicate records.\n")
    
    # Remove duplicates, keeping the first occurrence
    df <- distinct(df, user_id, .keep_all = TRUE)
    
    cat("Duplicates removed.\n")
  } else {
    cat("No duplicates found.\n")
  }
}

# ============================================================================
# Step 5: Correct corrupted categories
# ============================================================================
cat("\n--- Step 5: Correcting corrupted categories ---\n")

if ("country" %in% colnames(df)) {
  # Show the distribution before correction
  cat("\nCountry values before correction:\n")
  print(table(df$country))
  
  # Standardize country names
  df$country <- trimws(tolower(df$country))
  
  # Map all USA variants to "USA"
  df$country[df$country %in% c(
    "usa",
    "us",
    "u.s.a",
    "united states"
  )] <- "USA"
  
  # Capitalize properly
  #df$country <- stringr::str_to_title(df$country)
  df$country = toupper(df$country)
  
  cat("\nCountry values after correction:\n")
  print(table(df$country))
}

# ============================================================================
# Final overview of cleaned data
# ============================================================================
cat("\n--- Final Data Summary ---\n")
cat("Total rows:", nrow(df), "\n")
cat("Total columns:", ncol(df), "\n")
cat("\nData types after cleaning:\n")
print(str(df))

# ============================================================================
# OUTPUT: Save cleaned data to CSV
# ============================================================================
cat("\n--- Saving cleaned data ---\n")

# Generate output filename
output_file <- sub("\\.csv$", "_CLEAN.csv", input_file)

# Write the cleaned dataframe to CSV
write_csv(df, output_file)

cat("✓ Cleaned data saved to:", output_file, "\n")
cat("\n--- Data cleaning complete! ---\n")
