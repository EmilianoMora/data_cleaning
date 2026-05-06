# Social Media User Behavior Dataset — Complete R Tutorial

This tutorial provides a **comprehensive, step-by-step guide** to exploring, querying, and manipulating the *Social Media User Behavior Dataset* using **R**.

It is designed in a practical, hands-on style similar to real-world data cleaning workflows, covering:

- Data Loading & Setup
- Data Exploration 
- Data Selection & Filtering
- Data Manipulation & Transformation
- Handling Missing Data
- Data Aggregation & Summarization
- String Cleaning with Regular Expressions
- Reshaping Data with Pivot Functions
- Joining Multiple Datasets
- Basic Visualization with *ggplot*
---

## Environment Setup

Before starting, install and load the required packages.

```r
install.packages("tidyverse")
install.packages("janitor")
install.packages("stringr")

library(tidyverse)      # Core data manipulation (dplyr, ggplot2, readr, tidyr)
library(janitor)        # Clean column names and quick tabulations
library(stringr)        # String manipulation and regex functions
```
---
## Loading the Dataset
```r
# Set working directory (optional)
setwd("path/to/your/folder")

# Load dataset
data <- read.csv("social_media_user_behavior.csv", stringsAsFactors = FALSE)
```
---
## Clean column names
```r
data <- clean_names(data)

# Inspect column names
colnames(data)
```
## Initial Data Exploration
Understanding your dataset is the first critical step.
```r
# Structure and summary
str(data)
summary(data)
glimpse(data)

# Dimensions
dim(data)      # rows, columns
nrow(data)
ncol(data)

# Preview data
head(data, 10)
tail(data, 10)
```
---
## Explore categorical variables
```r
table(data$primary_platform)
table(data$gender)
```
## Explore numeric variables
```r
summary(data$age)
summary(data$daily_usage_hours)
```
---
## Quick visualization
```r
ggplot(data, aes(x = primary_platform)) +
  geom_bar() +
  theme_minimal() +
  labs(title = "User Distribution by Platform")
```
---
## Data Selection & Filtering
```r
# Selecting columns
data %>%
  select(user_id, age, primary_platform)

#Dropping columns
data %>%
  select(-country, -preferred_device)

# Filtering rows
# Single condition
data %>%
  filter(age > 25)

# Multiple conditions
data %>%
  filter(age > 25, primary_platform == "Instagram")

# Using OR condition
data %>%
  filter(primary_platform == "Instagram" | primary_platform == "Twitter")

# Sorting data (Ascending)
data %>%
  arrange(age)

# Sorting data (Descending)
data %>%
  arrange(desc(daily_usage_hours))
```
---
## Data Manipulation
```r
# Creating new variables
data <- data %>%
  mutate(
    age_group = ifelse(age < 25, "Young", "Adult"),
  )

# Conditional transformations
data <- data %>%
  mutate(
    usage_level = case_when(
      daily_usage_hours > 3 ~ "High",
      daily_usage_hours > 1 ~ "Medium",
      TRUE ~ "Low"
    )
  )

# Renaming variables
data <- data %>%
  rename(
    user_age = age,
    platform_name = primary_platform
  )

# Reordering columns
data <- data %>%
  select(user_id, user_age, everything())

# Removing duplicates
data <- data %>%
  distinct()
```
---
## Handling Missing Data
Missing data is common and critical to handle properly.
```r
# Detect missing values
colSums(is.na(data))

# Percentage of missing values
colMeans(is.na(data)) * 100

# Remove rows with missing values in specific columns
data_clean <- data %>%
  drop_na(user_age, platform_name)

# Replace missing values with mean
data <- data %>%
  mutate(
    user_age = ifelse(is.na(user_age), mean(user_age, na.rm = TRUE), user_age)
  )

# Replace with median
data <- data %>%
  mutate(
    daily_usage_hours = ifelse(is.na(daily_usage_hours),
                        median(daily_usage_hours, na.rm = TRUE),
                        daily_usage_hours)
  )

# Replace categorical NA
data <- data %>%
  mutate(
    location = replace_na(country, "Unknown")
  )
```
---
## Data Aggregation & Summarization
Aggregation helps extract insights and patterns.
```r
# Group and summarize
data %>%
  group_by(platform_name) %>%
  summarise(
    avg_time = mean(daily_usage_hours, na.rm = TRUE),
    total_users = n()
  )

# Multiple grouping variables
data %>%
  group_by(platform_name, gender) %>%
  summarise(
    avg_time = mean(daily_usage_hours, na.rm = TRUE),
    users = n()
  )

# Count occurrences
data %>%
  count(platform_name, sort = TRUE)

# Advanced summaries
data %>%
  group_by(platform_name) %>%
  summarise(
    min_time = min(daily_usage_hours, na.rm = TRUE),
    max_time = max(daily_usage_hours, na.rm = TRUE),
    median_time = median(daily_usage_hours, na.rm = TRUE),
    sd_time = sd(daily_usage_hours, na.rm = TRUE)
  )

# Add aggregated values back to dataset
data <- data %>%
  group_by(platform_name) %>%
  mutate(
    avg_platform_time = mean(daily_usage_hours, na.rm = TRUE)
  )
```
---
## Piping
The %>% operator allows chaining operations for clarity.
```r
data %>%
  filter(user_age > 20) %>%
  select(user_id, platform_name, daily_usage_hours) %>%
  arrange(desc(daily_usage_hours))
```
---
## String Cleaning with Regular Expressions

Regular expressions (regex) are powerful tools for pattern matching and string manipulation. The `stringr` package provides user-friendly functions for working with strings.

### Basic String Detection and Extraction

```r
# Detect if a string matches a pattern
str_detect(data$email, "@gmail\\.com")      # Returns TRUE/FALSE
str_detect(data$username, "^[A-Z]")         # Starts with uppercase letter

# Filter rows based on string patterns
data %>%
  filter(str_detect(email, "@gmail\\.com"))

# Extract parts of strings using regex
str_extract(data$email, "[a-zA-Z0-9]+")     # Extract first alphanumeric sequence
str_extract_all(data$bio, "\\d+")           # Extract all numbers
```

### Common Regular Expression Patterns

| Pattern | Meaning | Example |
|---------|---------|---------|
| `.` | Any character | `a.c` matches "abc", "adc" |
| `\d` | Digit (0-9) | `\\d{3}` matches "123" |
| `\w` | Word character (a-z, A-Z, 0-9, _) | `\\w+` matches "user_123" |
| `\s` | Whitespace | `hello\\sworld` matches "hello world" |
| `^` | Start of string | `^user` matches "user123" but not "theuser" |
| `$` | End of string | `123$` matches "abc123" but not "123abc" |
| `[abc]` | Any character in brackets | `[aeiou]` matches any vowel |
| `[a-z]` | Character range | `[0-9]` matches any digit |
| `+` | One or more | `a+` matches "a", "aa", "aaa" |
| `*` | Zero or more | `a*b` matches "b", "ab", "aab" |
| `?` | Zero or one | `a?b` matches "b", "ab" |
| `{n,m}` | Between n and m times | `a{2,4}` matches "aa", "aaa", "aaaa" |
| `\|` | OR operator | `cat\|dog` matches "cat" or "dog" |
| `()` | Group | `(ab)+` matches "ab", "abab" |

### Replace and Clean Strings

```r
# Replace first occurrence
str_replace(data$location, "UAE", "United Arab Emirates")

# Replace all occurrences
str_replace_all(data$sleep_disrupttion, " ", "_")

# Remove specific patterns
data <- data %>%
  mutate(
    username_clean = str_remove(username, "@"),
    phone_clean = str_remove_all(phone, "[^0-9]")  # Keep only digits
  )

# Clean email addresses (lowercase and trim whitespace)
data <- data %>%
  mutate(
    email = str_trim(email) %>% str_to_lower()
  )

# Standardize platform names (handle typos and variations)
data <- data %>%
  mutate(
    platform = case_when(
      str_detect(platform, "(?i)insta") ~ "Instagram",  # (?i) = case insensitive
      str_detect(platform, "(?i)twitter|tweet") ~ "Twitter",
      str_detect(platform, "(?i)facebook|fb") ~ "Facebook",
      TRUE ~ platform
    )
  )
```

### Extract Information from Complex Strings

```r
# Extract date components from account_join_date strings
data <- data %>%
  mutate(
    year = str_extract(account_join_date, "\\d{4}"),
    month = str_extract(account_join_date, "(?<=-)[0-9]{2}"),
    date_clean = str_extract(account_join_date, "^[0-9]{4}-[0-9]{2}-[0-9]{2}")
  )

# Extract numerical values from text
data <- data %>%
  mutate(
    post_count = as.numeric(str_extract(preferred_content_type, "\\d+"))
  )

# Split strings and create new columns
data <- data %>%
  separate(sleep_disruption, 
           into = c("1st_impact", "2nd_impact"), 
           sep = "_",
           remove = FALSE)
```
---
## Reshaping Data with Pivot Functions

Real-world data often comes in formats that aren't ideal for analysis. Reshaping data from **long to wide format** (and vice versa) is essential for exploratory analysis and visualization.

### Understanding Long vs Wide Format

**Wide Format** (each variable in its own column):
```
platform     instagram_users    twitter_users    facebook_users
2024-01        1500               800              2000
2024-02        1650               850              2100
```

**Long Format** (variables in rows):
```
date       platform      users
2024-01    instagram     1500
2024-01    twitter       800
2024-01    facebook      2000
2024-02    instagram     1650
```

### Converting Wide to Long with `pivot_longer()`

```r
# Basic conversion: make data longer
data_long <- data_wide %>%
  pivot_longer(
    cols = c(instagram_users, twitter_users, facebook_users),
    names_to = "platform",
    values_to = "users"
  )

# More practical example with the social media data
# Assume data has columns: user_id, date, instagram_time, twitter_time, facebook_time
usage_long <- data %>%
  pivot_longer(
    cols = starts_with("instagram_") | starts_with("twitter_") | starts_with("facebook_"),
    names_to = "platform_metric",
    values_to = "value"
  ) %>%
  separate(platform_metric, 
           into = c("platform", "metric"),
           sep = "_")

# Select specific columns and transform
daily_activity <- data %>%
  pivot_longer(
    cols = monday:sunday,
    names_to = "day_of_week",
    values_to = "time_spent"
  )

# Remove NA values while pivoting
engagement_long <- data %>%
  pivot_longer(
    cols = likes:shares,
    names_to = "engagement_type",
    values_to = "count",
    values_drop_na = TRUE
  )
```

### Converting Long to Wide with `pivot_wider()`

```r
# Basic conversion: make data wider
data_wide <- data_long %>%
  pivot_wider(
    names_from = platform,
    values_from = users
  )

# Real-world example: create a user-platform usage matrix
usage_matrix <- data %>%
  group_by(user_id, platform) %>%
  summarise(total_time = sum(time_spent, na.rm = TRUE), .groups = "drop") %>%
  pivot_wider(
    names_from = platform,
    values_from = total_time,
    values_fill = 0  # Fill missing values with 0
  )

# Create aggregated summary table
summary_wide <- data %>%
  group_by(platform, gender) %>%
  summarise(
    avg_age = mean(age, na.rm = TRUE),
    avg_time = mean(time_spent, na.rm = TRUE),
    user_count = n(),
    .groups = "drop"
  ) %>%
  pivot_wider(
    names_from = gender,
    values_from = c(avg_age, avg_time, user_count),
    names_sep = "_"
  )

# Handle multiple value columns with aggregation
platform_stats <- data %>%
  group_by(platform, age_group) %>%
  summarise(
    mean_time = mean(time_spent, na.rm = TRUE),
    median_time = median(time_spent, na.rm = TRUE),
    user_count = n(),
    .groups = "drop"
  ) %>%
  pivot_wider(
    names_from = age_group,
    values_from = c(mean_time, median_time, user_count),
    names_sep = "_"
  )
```

### Advanced Pivoting Patterns

```r
# Pivot multiple value columns
data_wide <- data_long %>%
  pivot_wider(
    names_from = platform,
    values_from = c(users, engagement_rate),
    names_sep = "_"
  )

# Create a comparison matrix
comparison <- data %>%
  pivot_wider(
    id_cols = user_id,
    names_from = platform,
    values_from = time_spent,
    values_fill = 0
  ) %>%
  mutate(
    total_time = rowSums(across(where(is.numeric))),
    top_platform = names(.[2:4])[apply(.[2:4], 1, which.max)]
  )

# Pivot with custom names using names_glue
data_custom <- data_long %>%
  pivot_wider(
    names_from = c(platform, metric),
    values_from = value,
    names_glue = "{platform}_{metric}"
  )

# Unpivot and reshape with functions
nested_summary <- data %>%
  pivot_longer(
    cols = -user_id,
    names_to = "metric",
    values_to = "value"
  ) %>%
  group_by(metric) %>%
  summarise(
    mean = mean(value, na.rm = TRUE),
    sd = sd(value, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  pivot_wider(
    names_from = metric,
    values_from = c(mean, sd)
  )
```

### Complete Example: Reshape and Analyze

```r
# Load and reshape daily activity data
daily_data <- read.csv("daily_activity.csv")

activity_analysis <- daily_data %>%
  # Convert from wide to long format
  pivot_longer(
    cols = starts_with("day_"),
    names_to = "day",
    names_prefix = "day_",
    values_to = "time_spent"
  ) %>%
  
  # Clean and transform
  mutate(
    day = factor(day, 
                 levels = c("monday", "tuesday", "wednesday", "thursday", 
                           "friday", "saturday", "sunday")),
    platform = str_to_title(platform)
  ) %>%
  
  # Summarize
  group_by(platform, day) %>%
  summarise(
    avg_time = mean(time_spent, na.rm = TRUE),
    median_time = median(time_spent, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  
  # Convert back to wide for comparison
  pivot_wider(
    names_from = day,
    values_from = avg_time
  )

# Visualize the pivoted data
activity_analysis %>%
  pivot_longer(cols = -platform, names_to = "day", values_to = "avg_time") %>%
  ggplot(aes(x = day, y = avg_time, fill = platform)) +
  geom_col(position = "dodge") +
  theme_minimal() +
  labs(title = "Average Time Spent by Platform and Day",
       x = "Day of Week",
       y = "Average Time (minutes)")
```

---
## Joining Multiple Datasets
In real-world projects, data is often split across multiple tables. R (via dplyr) provides several join functions similar to SQL.
```r
# Create a Second Dataset
user_info <- data.frame(
  user_id = c("USR00001", "USR00002", "USR00003", "USR00004"),
  country = c("UK", "USA", "UAE", "Pakistan")
)
```
### Inner Join
Returns only matching rows in both datasets.
```r
inner_join(data, user_info, by = "user_id")
```
### Left Join
Keeps all rows from the main dataset (data), adds matches from user_info.
```r
left_join(data, user_info, by = "user_id")
```
### Right Join
Keeps all rows from user_info.
```r
right_join(data, user_info, by = "user_id")
```
### Full Join
Keeps all rows from both datasets.
```r
full_join(data, user_info, by = "user_id")
```
### Join on Different Column Names
```r
left_join(data, user_info, by = c("user_id" = "user_id"))
```
### Multiple Key Join
```r
left_join(data, user_info, by = c("user_id", "platform"))
```
### Anti Join (Find non-matching rows)
```r
anti_join(data, user_info, by = "user_id")
```
### Semi Join (Filter matching rows only)
```r
semi_join(data, user_info, by = "user_id")
```
---
## Basic Visualization
```r
ggplot(data, aes(x = user_age, y = daily_usage_hours)) +
  geom_point(alpha = 0.6) +
  geom_smooth(method = "lm") +
  theme_minimal() +
  labs(
    title = "Age vs Time Spent on Social Media",
    x = "Age",
    y = "Time Spent (minutes)"
  )
```
