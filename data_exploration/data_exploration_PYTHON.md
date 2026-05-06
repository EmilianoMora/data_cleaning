# Social Media User Behavior Dataset — Complete Python Tutorial

This tutorial provides a **comprehensive, step-by-step guide** to exploring, querying, and manipulating the *Social Media User Behavior Dataset* using **Python**.

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
- Basic Visualization with *matplotlib* and *seaborn*
---

## Environment Setup

Before starting, install and import the required packages.

```python
pip install pandas numpy matplotlib seaborn
```
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
```
# Optional settings
```python
pd.set_option('display.max_columns', None)
sns.set(style="whitegrid")
```
Loading the Dataset
# Set working directory (optional)
```python
import os
os.chdir("path/to/your/folder")

# Load dataset
data = pd.read_csv("social_media_user_behavior.csv")
Clean column names
# Convert to lowercase and replace spaces with underscores
data.columns = (
    data.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)
```
# Inspect column names
```python
data.columns
```
---
# Initial Data Exploration
# Structure and summary
```python
data.info()
data.describe(include='all')
```
# Dimensions
```python
data.shape      # rows, columns
len(data)       # number of rows
data.shape[1]   # number of columns
```
# Preview data
```python
data.head(10)
data.tail(10)
```
# Explore categorical variables
```python
data['primary_platform'].value_counts()
data['gender'].value_counts()
```
# Explore numeric variables
```python
data['age'].describe()
data['daily_usage_hours'].describe()
```
# Quick visualization
```python
sns.countplot(data=data, x='primary_platform')
plt.title("User Distribution by Platform")
plt.xticks(rotation=45)
plt.show()
```
---
# Data Selection & Filtering
# Selecting columns
```python
data[['user_id', 'age', 'primary_platform']]
```
# Dropping columns
```python
data.drop(columns=['country', 'preferred_device'])
```
# Filtering rows
# Single condition
```python
data[data['age'] > 25]
```
# Multiple conditions
```python
data[(data['age'] > 25) & (data['primary_platform'] == "Instagram")]
```
# Using OR condition
```python
data[(data['primary_platform'] == "Instagram") | (data['primary_platform'] == "Twitter")]
```
# Sorting data (Ascending)
```python
data.sort_values(by='age')
```
# Sorting data (Descending)
```python
data.sort_values(by='daily_usage_hours', ascending=False)
```
---
# Data Manipulation
# Creating new variables
```python
data['age_group'] = np.where(data['age'] < 25, "Young", "Adult")
```
# Conditional transformations
```python
data['usage_level'] = np.select(
    [
        data['daily_usage_hours'] > 3,
        data['daily_usage_hours'] > 1
    ],
    ["High", "Medium"],
    default="Low"
)
```
# Renaming variables
```python
data = data.rename(columns={
    'age': 'user_age',
    'primary_platform': 'platform_name'
})
```
# Reordering columns
```python
cols = ['user_id', 'user_age'] + [col for col in data.columns if col not in ['user_id', 'user_age']]
data = data[cols]
```
# Removing duplicates
```python
data = data.drop_duplicates()
```
---
# Handling Missing Data
# Detect missing values
```python
data.isna().sum()
```
# Percentage of missing values
```python
data.isna().mean() * 100
```
# Remove rows with missing values in specific columns
```python
data_clean = data.dropna(subset=['user_age', 'platform_name'])
```
# Replace missing values with mean
```python
data['user_age'] = data['user_age'].fillna(data['user_age'].mean())
```
# Replace with median
```python
data['daily_usage_hours'] = data['daily_usage_hours'].fillna(data['daily_usage_hours'].median())
```
# Replace categorical NA
```python
data['location'] = data['country'].fillna("Unknown")
```
---
# Data Aggregation & Summarization
# Group and summarize
```python
data.groupby('platform_name').agg(
    avg_time=('daily_usage_hours', 'mean'),
    total_users=('user_id', 'count')
).reset_index()
```
# Multiple grouping variables
```python
data.groupby(['platform_name', 'gender']).agg(
    avg_time=('daily_usage_hours', 'mean'),
    users=('user_id', 'count')
).reset_index()
```
# Count occurrences
```python
data['platform_name'].value_counts()
```
# Advanced summaries
```python
data.groupby('platform_name')['daily_usage_hours'].agg(['min', 'max', 'median', 'std'])
```
# Add aggregated values back to dataset
```python
data['avg_platform_time'] = data.groupby('platform_name')['daily_usage_hours'].transform('mean')
```
# Method Chaining (Piping Equivalent)
```python
data.loc[data['user_age'] > 20, ['user_id', 'platform_name', 'daily_usage_hours']] \
    .sort_values(by='daily_usage_hours', ascending=False)
```
# Replace all occurrences
```python
data['sleep_disruption'] = data['sleep_disruption'].str.replace(" ", "_")
```
# Remove patterns
```python
data['username_clean'] = data['username'].str.replace("@", "", regex=False)
data['phone_clean'] = data['phone'].str.replace(r'[^0-9]', '', regex=True)
```
# Standardize platform names
```python
data['platform'] = np.select(
    [
        data['platform'].str.contains(r'(?i)insta', na=False),
        data['platform'].str.contains(r'(?i)twitter|tweet', na=False),
        data['platform'].str.contains(r'(?i)facebook|fb', na=False)
    ],
    ["Instagram", "Twitter", "Facebook"],
    default=data['platform']
)
```
---
# Extract Information from Complex Strings
# Extract date components
```python
data['year'] = data['account_join_date'].str.extract(r'(\d{4})')
data['month'] = data['account_join_date'].str.extract(r'-(\d{2})')
data['date_clean'] = data['account_join_date'].str.extract(r'^(\d{4}-\d{2}-\d{2})')
```
# Extract numeric values
```python
data['post_count'] = data['preferred_content_type'].str.extract(r'(\d+)').astype(float)
```
# Split columns
```python
data[['impact_1', 'impact_2']] = data['sleep_disruption'].str.split('_', expand=True)
```
Reshaping Data with Pivot Functions
Converting Wide to Long
```python
data_long = pd.melt(
    data_wide,
    value_vars=['instagram_users', 'twitter_users', 'facebook_users'],
    var_name='platform',
    value_name='users'
)

usage_long = pd.melt(
    data,
    id_vars=['user_id'],
    var_name='platform_metric',
    value_name='value'
)

usage_long[['platform', 'metric']] = usage_long['platform_metric'].str.split('_', expand=True)
```
Converting Long to Wide
```python
data_wide = data_long.pivot(index=None, columns='platform', values='users')

usage_matrix = data.groupby(['user_id', 'platform'])['time_spent'].sum().unstack(fill_value=0)

summary_wide = data.groupby(['platform', 'gender']).agg(
    avg_age=('age', 'mean'),
    avg_time=('time_spent', 'mean'),
    user_count=('user_id', 'count')
).unstack()
```
---
# Joining Multiple Datasets
# Create second dataset
```python
user_info = pd.DataFrame({
    'user_id': ["USR00001", "USR00002", "USR00003", "USR00004"],
    'country': ["UK", "USA", "UAE", "Pakistan"]
})
```
# Inner Join
```python
pd.merge(data, user_info, on='user_id', how='inner')
```
# Left Join
```python
pd.merge(data, user_info, on='user_id', how='left')
```
# Right Join
```python
pd.merge(data, user_info, on='user_id', how='right')
```
# Full Join
```python
pd.merge(data, user_info, on='user_id', how='outer')
```
# Anti Join
```python
data[~data['user_id'].isin(user_info['user_id'])]
```
# Semi Join
```python
data[data['user_id'].isin(user_info['user_id'])]
```
# Basic Visualization
```python
sns.scatterplot(data=data, x='user_age', y='daily_usage_hours', alpha=0.6)
# Add regression line
sns.regplot(data=data, x='user_age', y='daily_usage_hours', scatter=False)

plt.title("Age vs Time Spent on Social Media")
plt.xlabel("Age")
plt.ylabel("Time Spent (minutes)")
plt.show()
```
