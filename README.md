# data_cleaning

This repository is aimed to store basic data cleaning scripts (mostly for personal use).

Through many years of doing data analyses for my master's, PhD, and postdoc, I have developed many scripts to help me check the quality of the data in a database and spot common mistakes. However, all the scripts I created were specific to the datasets I was working with, making them difficult to reuse or share.

In order to make it easier for me and not make it specific to some of the datasets I used, I am using a completely new dataset and try to introduce several of the common mistakes I've found in my data. This way, the scripts become more general and applicable to various datasets.

## Table of Contents
- [Download a dataset](#download-a-dataset)
- [Introducing errors in the database](#introducing-errors-in-the-database)
- [Start the data cleaning process with R](#start-the-data-cleaning-process-with-r)
  - [Used packages](#used-packages)
  - [Load data](#load-data)
  - [Get basic overview of the data](#get-basic-overview-of-the-data)
  - [Detecting fake NA entries](#detecting-fake-na-entries)
  - [Some error in scoring](#some-error-in-scoring)
  - [Eliminating rows with NA's](#eliminating-rows-with-nas)
  - [Identify duplicated data](#identify-duplicated-data)
  - [Correct corrupted categories](#correct-corrupted-categories)

## Download a dataset

The dataset that I will be using was downloaded from [kaggle.com](https://www.kaggle.com). This webpage hosts a wide variety of databases on very different topics.

For the exercises in this repository, I will be using the *Social Media User Behavior Dataset*. This dataset was synthetically generated, so it is not true data. More information about the dataset can be found [here](https://www.kaggle.com/datasets/hamnamunir/social-media-user-behavior-dataset).

In order to download the data, I used the following command:

```sh
curl -L -o ~/Downloads/social-media-user-behavior-dataset.zip\
  https://www.kaggle.com/api/v1/datasets/download/hamnamunir/social-media-user-behavior-dataset
```

## Introducing errors in the database

In order to introduce messiness into the dataset, I used custom Python code to introduce some common errors such as the inclusion of some duplicated entries and the corruption of some categorical values:

```py
import pandas as pd
import numpy as np

# Load your data
df = pd.read_csv("~/Downloads/social-media-user-behavior-dataset/social_media_user_behavior.csv")

# Change only SOME existing "USA" values to "U.S.A"
variants = ["U.S.A", "US", "United States", "usa"]
mask = df["country"] == "USA"
rows = df[mask].sample(frac=0.32).index

df.loc[rows, "country"] = np.random.choice(
    variants,
    size=len(rows)
)

# Add duplicates by sampling 20 entries randomly and then concatenating it to the dataframe
duplicates = df.sample(frac=0.01)
df = pd.concat([df, duplicates])

df.to_csv("~/Downloads/social-media-user-behavior-dataset/social_media_user_behavior_UGLY.csv", index=False)
```

Alternatively, you can use [*Ugly CSV generator*](https://github.com/LucaCappelletti94/ugly_csv_generator), which is a Python package that introduces automated non-destructive errors.

To install *Ugly CSV generator* just run the following command:

```sh
pip install ugly_csv_generator
```

To introduce the errors, we can use the following commands in Python. A description of all the error types (i.e., available uglifications) can be found [here](https://github.com/LucaCappelletti94/ugly_csv_generator):

```py
import pandas as pd
from ugly_csv_generator import uglify

df = pd.read_csv("~/Downloads/social-media-user-behavior-dataset/social_media_user_behavior_UGLY.csv")

df["zero"] = 0

ugly = uglify(
    df,
    empty_columns = False,
    empty_rows = True,
    duplicate_schema = False,
    empty_padding = False,
    nan_like_artefacts = True,
    replace_zeros = True,
    replace_ones = True,
    satellite_artefacts = False,
    random_spaces = False,
    include_unicode = False,
    verbose = True,
    seed = 42,
)

ugly.to_csv("~/Downloads/social-media-user-behavior-dataset/social_media_user_behavior_UGLY_2.csv", index=False)
```

## Start the data cleaning process with R

### Used packages

In order to perform all of the data cleaning, I used the following R packages:

```R
library(tidyverse)
library(data.table)
library(lubridate)
library(stringr)
library(ggplot2)
library(janitor)
library(skimr)
library(corrplot)
```

### Load data

```R
setwd("~/Downloads/social-media-user-behavior-dataset")
df <- read_csv("social_media_user_behavior_UGLY_2.csv", col_names = T)
```

### Get basic overview of the data

```R
# Check memory usage
format(object.size(df), units = "MB")

# Get basic dataset overview
dim(df)

colnames(df) #Check column names

head(df) #See first lines of the dataframe
tail(df) #See last lines of the dataframe

sample_n(df, 5) #Sample 5 random rows

# The following three give us the type of strings in each column. They give more or less similar information.
str(df)
summary(df)
sapply(df, class)
```

### Detecting fake NA entries

From the `str()` command we can see that all the columns have string characters (i.e., `chr`). However, seeing the values of some of these columns, we can see that some of them should have numeric values. For example, the age column should be numeric. Let's try to convert it:

```
> df$age <- as.numeric(df$age)
Warning message:
NAs introduced by coercion 
```

We can take a look at the data in this column to see where the error is:

```
> as.numeric(df$age)
   [1]  NA  30  25  32  39  25  25  39  NA  33  23  31  23  NA  23  28  13  NA  13  NA  22  NA  NA  18  29  NA  NA  19  NA  NA  15  38  25  NA  27  15  22  27  17  30  NA
  [42]  22  24  NA  NA  22  41  26  NA  18  NA  NA  NA  33  17  NA  28  13  NA  16  NA  NA  28  32  NA  28  26  24  NA  15  21  23  35  29  NA  13  29  NA  23  NA  21  31
  [83]  35  34  20  24  29  NA  34  23  25  NA  18  17  33  37  NA  26  35  29  NA  21  NA  29  NA  39  26  39  13  33  NA  27  24  27  NA  13  NA  25  NA  29  38  22  20
 [124]  22  34  29  22  31  NA  27  34  21  NA  24  23  15  29  29  27  NA  25  NA  15  23  24  20  25  NA  30  42  28  NA  29  26  13  NA  26  27  46  25  29  26  17  36
 [165]  33  NA  NA  33  19  38  NA  15  31  44  19  22  27  22  NA  NA  14  NA  27  18  30  19  NA  39  20  NA  24  NA  33  17  NA  28  NA  NA  37  14  NA  28  NA  29  33
 [206]  17  16  31  29  29  29  21  28  29  21  NA  NA  41  30  NA  17  32  19  33  36  NA  NA  20  NA  NA  NA  34  30  33  42  25  NA  20  19  20  26  NA  29  29  33  NA
 [247]  NA  NA  27  38  NA  NA  24  48  NA  32  NA  20  18  30 NaN  NA  25  32  30  26  20  14  NA  23  33  NA  28  17  28  30  19  28  27  17  29  NA  NA  31  35  35  NA
 [288]  NA  15  19  31  NA  31  31  NA  57 NaN  31  NA  36  34  32  24  33  20  NA  NA  NA  25  23  27  NA  45  NA  13  32  NA  14  23  NA  NA  NA  NA  NA  35  27  18  21
 [329]  32  21  28  27  NA  21  44  32  13  28  21  33  20  26  NA  31  33  NA  17  24  23  21  NA  41  30  16  34  43  NA  NA  35  14  23  NA  37  21  30  33  19  NA  NA
 [370]  26  13  18  NA  NA  24  17  40  15  23  28  38  15  36  NA  27 NaN  NA  19  30  28  22  NA  27  23  27  32  39  17  44  13  25  31  29  22  25  23  22  33  29  21
 [411]  34  29  33  NA  32  20  NA  22  32  31 NaN  26  27  37  22  31  25 NaN  25  NA  35  33  33  37  27  NA  32  NA  24  29  25  27  31  20  43  18  17  36  33  NA  31
 [452]  32  26  NA  NA  19  NA  NA  27  21  34  NA  25  NA  20  24  NA  30  22  NA  20  NA  28  28  22  NA  23  28  NA  15  15  21  25  29  38   0  NA  33  NA  25  26  18
 [493]  26  24  29 NaN  20  31  NA  NA  39  26  30 NaN  32  NA  23  NA  NA  NA  28  NA  27 NaN  27  20  NA  NA  27  NA  30  38  34  44  NA  NA  20  33  28  44  20  20  22
 [534]  13  22  NA  20  28  NA  29  42  34  NA  NA  22  19  NA  NA  30  NA  16 NaN  NA  41  36  23  13  37  26  36  14  NA  22  NA  27  27  23  NA  NA  NA  31  18  NA  NA
 [575]  25  NA  27  NA  31  NA  32  18   0  NA  14  37 NaN  29  21  39  27  NA  36  27  NA  43  41  NA  25  NA  34  32  37  19  32  NA  35  NA  NA  13  NA  17  13  NA  NA
 [616]  24  32  39  27  NA  40  15  NA  13  26  30  NA  26  13  26  NA  16  32  29  19  22  18  26  34  19   0  NA  31  22  20  26  18  22  17  42  NA  27  21  NA  NA  NA
 [657]  NA  28  26  25  31  NA  33  NA  22  22  24  NA  13  14  37  40  25  NA  31  29  NA  NA  51  NA  35  NA  25  NA  19  14  28  NA  20  15  21  18  40  34  26  38  27
 [698]  NA  20  NA  NA  39  31  NA  18  25  NA  NA  19  NA  15  34  NA  42  15  31  21  NA  23  22  NA  NA  20  NA  27  20  29  26  25  19  22  33  31  19  27  NA  NA   0
 [739]  NA  33  13  31  21  31  NA  20  13  NA  13  27  29  NA  19  NA  32  13  26  17  NA  21  27  20  23  35  22  33  17  NA  31  38  13  20  NA   0  31  25  29  22  27
 [780]  25  36  29  NA  29  NA  NA  23  NA  23  NA  23  30  23  29  43  33  24  36  NA  NA  23  13  18  13  NA  24  27  40  29  25  33  13  NA  28  33  NA  NA  15  36  NA
 [821]  29  23  32  NA  45  28  28  23  20  NA  NA  33  NA  NA  20  27  NA  23  NA  30  29  35 NaN  22  NA  24  NA  19  23  30  33  19  33  37  30  42  20  17   0  13  NA
 [862]  38  32  26  NA  NA  29  17  46  28  27  32  30  28  20  30  42  37  39  22  NA  19  NA  25  27  35  13  39  25  NA  NA  23  18  13  33  27  NA  NA   0  16  NA  16
 [903]  24  40  NA  NA  24  NA  14  25  24  NA  NA  13  26  25  32  41  36  24  18  NA  47  NA  NA  27  27  26  NA  28  NA NaN  25  22  22  26  NA  NA  22  21  27  24  NA
 [944]  NA  39  13  35  NA  36  NA  NA  13  24  NA   0  24  15  20  18  41  34  37  NA  32  17  22  30  17  32  25  24 NaN  32  30  24  36  18  31  31  24  NA  29  16  NA
 [985]  NA  34  25  22  NA  NA  NA  NA  35  21  15  14  31  NA  NA  16
 [ reached getOption("max.print") -- omitted 1863 entries ]
Warning message:
NAs introduced by coercion
```

We can see that NA's are stored differently in this column. In this case they are found as `NA` or `NaN`. This is just in this column; it is likely that other columns have other ways to specify NA.

To detect all the different ways in which an NA can be found, I use the following command that gives you a list of all the potential ways in which an NA can be stored:

```R
different_ways_NAs <- unique(unlist(lapply(df, function(x) unique(x[grepl("^(na|nan|n/a|#n/a|#n/d|#RIF!|null|none|missing|nil|unknown|blank|\\.*|-+|/+|_+|\\?+)$", trimws(as.character(x)), ignore.case = TRUE)]))))
print(different_ways_NAs)
```

This command:
- Scans all columns
- Converts values to character
- Trims whitespace
- Detects common "fake NA" representations
- Returns the unique suspicious values found

The following code automatically detects all potential fake NA's and transforms them as proper NA's (empty space). If we run the original one-liner code above, we will see that now it should be empty:

```R
df[] <- lapply(df, function(x) {
  x <- trimws(as.character(x))
  x[grepl("^(na|nan|n/a|#n/a|#n/d|#RIF!|null|none|missing|nil|unknown|blank|\\.*|-+|/+|_+|\\?+)?$", x, ignore.case = TRUE)] <- NA
  x
})
```

Now we can convert the 'age' column to numeric without error:

```R
df$age <- as.numeric(df$age)
str(df)
```

**Note:** In some cases the NA is stored as a '0'. Whether or not a zero is an NA needs to be checked with the person that created the dataframe.

### Some error in scoring

Now, we can take a look at the column called *daily_usage_hours*. We can deduce that it should have numeric values. However, with the `str(df)` command, we can see that it is a character string. Let's check what values are in this column:

```R
table(df$daily_usage_hours)
```

From the results, we can see that there are some values that are not numbers, for example *I*, *l*, *o*, and *O*. It is likely that some of them are meant to be 1's and others are supposed to be 0's. Here's the output:

```
> table(df$daily_usage_hours)

   0  0.5  0.6  0.7  0.8  0.9    1  1.1  1.2  1.3  1.4  1.5  1.6  1.7  1.8  1.9 10.0 10.5 11.1 12.0  2.0  2.1  2.2  2.3 
  11   73   17   36   28   34   15   52   46   41   48   52   42   64   62   47    1    1    1    5   44   51   50   41 
 2.4  2.5  2.6  2.7  2.8  2.9  3.0  3.1  3.2  3.3  3.4  3.5  3.6  3.7  3.8  3.9  4.0  4.1  4.2  4.3  4.4  4.5  4.6  4.7 
  49   55   41   44   34   37   44   44   44   34   40   42   39   25   34   31   35   27   22   15   26   20   12   21 
 4.8  4.9  5.0  5.1  5.2  5.3  5.4  5.5  5.6  5.7  5.8  5.9  6.0  6.1  6.2  6.3  6.4  6.5  6.6  6.7  6.8  6.9  7.0  7.1 
  12   19   22   12   11   18   16   10   14    9   10   10    7   13    4    6    5    7    9   11   12    7    3    7 
 7.2  7.3  7.4  7.5  7.6  7.7  7.8  7.9  8.0  8.1  8.2  8.3  8.4  8.6  8.7  9.0  9.1  9.2  9.4  9.5  9.6  9.7  9.9    I 
   2    2    5    3    6    3    4    2    1    4    2    2    1    2    1    3    2    2    1    3    1    1    1   12 
   l    o    O 
  14    6    9 
```

We can use the following code to find which ones are not numbers, in case one is escaping from us:

```R
unique(df$daily_usage_hours[!grepl("^[0-9]*\\.?[0-9]+$", trimws(as.character(df$daily_usage_hours)))])
```

Depending on the information from the dataframe creator, we could choose to convert all the incorrect entries as NA:

```R
df$daily_usage_hours[
  !grepl("^[0-9]*\\.?[0-9]+$", trimws(as.character(df$daily_usage_hours)))
] <- NA
```

However, they may not be NA's. In this case I will convert the *l* and *I* to 1's and *o* and *O* to zeros:

```R
df$daily_usage_hours <- trimws(as.character(df$daily_usage_hours)) #Trim white spaces

df$daily_usage_hours[df$daily_usage_hours %in% c("I", "l")] <- "1"
df$daily_usage_hours[df$daily_usage_hours %in% c("o", "O")] <- "0"

df$daily_usage_hours <- as.numeric(df$daily_usage_hours)
```

We can also apply this correction to all columns automatically:

```R
df[] <- lapply(df, function(col) {
  
  col[col %in% c("I", "l")] <- "1"
  col[col %in% c("o", "O")] <- "0"
  
  suppressWarnings({
    num_col <- as.numeric(col)
    
    # Convert to numeric only if most values are numeric
    if(mean(!is.na(num_col)) > 0.8) {
      return(num_col)
    }
  })
  
  return(col)
})
```

### Eliminating rows with NA's

The uglification of the database introduced many rows with NA's that probably should be eliminated. In the case of this dataframe, the solution on which rows to eliminate is quite easy. We can eliminate rows where the user_id is 0 or a blank space:

```R
df <- filter(df, user_id != 0 ) %>%
  filter(user_id != " ")
```

### Identify duplicated data

I had included 20 duplicated rows. The easiest way to find them is by finding the duplicated entries in the *user_id* column because, in theory, there should only be one entry per user:

```R
if ("user_id" %in% colnames(df)) {
  
  dup_ids <- df %>%
    group_by(user_id) %>%
    filter(n() > 1)
  
  print(dup_ids)
}
```

To eliminate them we can use two approaches:

```R
# Method 1: Base R
df <- df[!duplicated(df$user_id), ]

# Method 2: Using dplyr
df <- distinct(df, user_id, .keep_all = TRUE)
```

### Correct corrupted categories

Using the following command, we can see that some categories should be collapsed into a single one. USA is written in different ways:

```R
> table(df$country)

    Australia        Brazil        Canada       Germany         India       Nigeria      Pakistan         U.S.A           UAE            UK United States            US           usa           USA
          144            91           163           138           323            97           369            17           182           179            30            25            28           214
```

The following code converts everything to lowercase temporarily, removes whitespace, and maps all U.S. variants to "USA":

```R
df$country <- trimws(tolower(df$country))

df$country[df$country %in% c(
  "usa",
  "us",
  "u.s.a",
  "united states"
)] <- "USA"
```

---

**Happy data cleaning!** If you have any questions or suggestions, feel free to open an issue or reach out.
