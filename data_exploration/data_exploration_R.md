# Social Media User Behavior Dataset — Complete R Tutorial

This tutorial provides a **comprehensive, step-by-step guide** to exploring, querying, and manipulating the *Social Media User Behavior Dataset* using **R**.

It is designed in a practical, hands-on style similar to real-world data cleaning workflows, covering:

- Data Loading & Setup
- Data Exploration 
- Data Selection & Filtering
- Data Manipulation & Transformation
- Handling Missing Data
- Data Aggregation & Summarization
- Workflow Best Practices
---

## Environment Setup

Before starting, install and load the required packages.

```r
install.packages("tidyverse")
install.packages("janitor")

library(tidyverse) #Core data manipulation (dplyr, ggplot2, readr)
library(janitor) #Clean column names and quick tabulations
```
## Loading the Dataset
```r
# Set working directory (optional)
setwd("path/to/your/folder")

# Load dataset
data <- read.csv("social_media_usage.csv", stringsAsFactors = FALSE)
```
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
## Explore categorical variables
```r
table(data$platform)
table(data$gender)
```
## Explore numeric variables
```r
summary(data$age)
summary(data$time_spent)
```
## Quick visualization
```r
ggplot(data, aes(x = platform)) +
  geom_bar() +
  theme_minimal() +
  labs(title = "User Distribution by Platform")
```
## Data Selection & Filtering
```r
# Selecting columns
data %>%
  select(user_id, age, platform)

#Dropping columns
data %>%
  select(-location, -device_type)

# Filtering rows
# Single condition
data %>%
  filter(age > 25)

# Multiple conditions
data %>%
  filter(age > 25, platform == "Instagram")

# Using OR condition
data %>%
  filter(platform == "Instagram" | platform == "Twitter")

# Sorting data
# Ascending
data %>%
  arrange(age)

# Descending
data %>%
  arrange(desc(time_spent))
```
## Data Manipulation
```r
# Creating new variables
data <- data %>%
  mutate(
    age_group = ifelse(age < 25, "Young", "Adult"),
    time_hours = time_spent / 60
  )

# Conditional transformations
data <- data %>%
  mutate(
    usage_level = case_when(
      time_spent > 180 ~ "High",
      time_spent > 60 ~ "Medium",
      TRUE ~ "Low"
    )
  )

# Renaming variables
data <- data %>%
  rename(
    user_age = age,
    platform_name = platform
  )

# Reordering columns
data <- data %>%
  select(user_id, user_age, everything())

# Removing duplicates
data <- data %>%
  distinct()
```
## Handling Missing Data
Missing data is common and critical to handle properly.
```r
# Detect missing values
colSums(is.na(data))

# Percentage of missing values
colMeans(is.na(data)) * 100

# Remove rows with ANY missing values
data_clean <- data %>%
  drop_na()

# Remove rows with missing values in specific columns
data_clean <- data %>%
  drop_na(age, platform)

# Replace missing values with mean
data <- data %>%
  mutate(
    age = ifelse(is.na(age), mean(age, na.rm = TRUE), age)
  )

# Replace with median
data <- data %>%
  mutate(
    time_spent = ifelse(is.na(time_spent),
                        median(time_spent, na.rm = TRUE),
                        time_spent)
  )

# Replace categorical NA
data <- data %>%
  mutate(
    location = replace_na(location, "Unknown")
  )
```
## Data Aggregation & Summarization
Aggregation helps extract insights and patterns.
```r
# Group and summarize
data %>%
  group_by(platform) %>%
  summarise(
    avg_time = mean(time_spent, na.rm = TRUE),
    total_users = n()
  )

# Multiple grouping variables
data %>%
  group_by(platform, gender) %>%
  summarise(
    avg_time = mean(time_spent, na.rm = TRUE),
    users = n()
  )

# Count occurrences
data %>%
  count(platform, sort = TRUE)

# Advanced summaries
data %>%
  group_by(platform) %>%
  summarise(
    min_time = min(time_spent, na.rm = TRUE),
    max_time = max(time_spent, na.rm = TRUE),
    median_time = median(time_spent, na.rm = TRUE),
    sd_time = sd(time_spent, na.rm = TRUE)
  )

# Add aggregated values back to dataset
data <- data %>%
  group_by(platform) %>%
  mutate(
    avg_platform_time = mean(time_spent, na.rm = TRUE)
  )
```
## Piping
The %>% operator allows chaining operations for clarity.
```r
data %>%
  filter(age > 20) %>%
  select(user_id, platform, time_spent) %>%
  arrange(desc(time_spent))
```
## Basic Visualization
```r
ggplot(data, aes(x = age, y = time_spent)) +
  geom_point(alpha = 0.6) +
  geom_smooth(method = "lm") +
  theme_minimal() +
  labs(
    title = "Age vs Time Spent on Social Media",
    x = "Age",
    y = "Time Spent (minutes)"
  )
```
