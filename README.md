# data_cleaning
This repository is aimed store basic data cleaning scripts (mostly for me)

Through many years of doing data analyses for my masters, PhD and posdoc, I have developed many scripts to help me check the quality of the data in a database and spot common mistakes. However, all these scripts and the knowledge within them are usually scatered in many different files. This repository is aimed at putting it in all together to keep track of them. 

In order to make it easier for me and not make it specific to some of the datasets I used, I am using a compelty new dataset and try to introduce several of the common mistakes I've found on my data sets.

## Download a dataset
The dataset that I will be using was downloaded from [kaggle.com](https://www.kaggle.com). This webpage hosts a wide variety of databases on very differerent topics.

For the excercises in this repository, I will be using the *Social Media User Behavior Dataset*. This dataset was syntehtically generated, so it is not true data. More information about the dataset can be found [here](https://www.kaggle.com/datasets/hamnamunir/social-media-user-behavior-dataset/data).

In order to download the data, I used the following command:
```sh
curl -L -o ~/Downloads/social-media-user-behavior-dataset.zip\
  https://www.kaggle.com/api/v1/datasets/download/hamnamunir/social-media-user-behavior-dataset
```
## Introducing errors in the database
In order to introduce messyness into the dataset, I used some custom python code to introduce some common errors such as the inclusion of some duplicated entries and the corruption of some categories.
```py
# Load your data
df = pd.read_csv("~/Downloads/social-media-user-behavior-dataset/social_media_user_behavior.csv")

# Add duplicates by sampling 20 entries randomly and then concatenating it to the dataframe
duplicates = df.sample(frac=0.01)
df = pd.concat([df, duplicates])

# Change only SOME existing "USA" values to "U.S.A"
variants = ["U.S.A", "US", "United States", "usa"]

mask = df["country"] == "USA"

rows = df[mask].sample(frac=0.3).index

df.loc[rows, "country"] = np.random.choice(
    variants,
    size=len(rows)
)
```

[*Ugly CSV generator*](https://github.com/LucaCappelletti94/ugly_csv_generator) which is a python package that introduces automated non-destructive errors.

To install *Ugly CSV generator* just run the following command:
```sh
pip install ugly_csv_generator
```

To run introduce the errors, we can use the following commands in python. A description of all the error types (i.e., available uglufications) can be found [here](https://github.com/LucaCappelletti94/ugly_csv_generator).
```py
import pandas as pd

df = pd.read_csv("~/Downloads/social-media-user-behavior-dataset/social_media_user_behavior.csv")

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

ugly.to_csv("~/Downloads/social-media-user-behavior-dataset/social_media_user_behavior_UGLY.csv", index=False)
```
## Start the datacleaning process with R
### Used packages
In order to make all of the data cleaning, I used the following R packages:
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
df <- read_csv("social_media_user_behavior_UGLY.csv", col_names = T)
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

# The following three gives us the type of strings in each column. They give moreless similar information.
str(df)
summary(df)
sapply(df, class)
```
### Detecting fake NA entries
From the str() command we can see that all the columns have string characters (i.e., chr). However, seeing the value sof some of these columns, we can see that some of them should have numeric values. For example, the columns: age, daily_usage_hours, followers_counts, etc. In one case, we can see that the column 'account_join_date' string should be a date, but is coded as a character. If we try to force some of the columns that are supposed to be numeric we will have an error:
```
> df$age <- as.numeric(df$age)
Warning message:
NAs introduced by coercion 
```
We can take a look at the data in this column to see where is the error:
```
> as.numeric(df$age)
   [1]  30  25  32  39  25  25  39  33  23  31  23  NA  23  28  13  13  22  NA  18  29  19  NA  NA  15  38  25  27  15  22
  [30]  27  17  30  22  24  NA  22  41  26  18  NA  NA  33  17  NA  28  13  16  28  32  28  26  24  NA  15  21  23  35  29
  [59]  13  29  23  NA  21  31  35  34  20  24  29  34  23  25  18  17  33  37  26  NA  35  29  21  NA  29  NA  39  26  39
  [88]  13  33  27  24  27  13  NA  25  29  NA  38  22  20  22  34  29  22  31  27  34  21  24  23  15  29  29  27  25  NA
 [117]  15  23  24  20  25  30  42  28  29  26  13  26  NA  27  46  25  NA  29  26  NA  17  36  33  33  19  38  NA  15  31
.
.
.
.
.
 [871]  16  19  35  19  NA  48  30  28  20  32  22  NA  27  47  26  36  21  26  41  21  41  32  NA  22  32  34  31  14  21
 [900]  NA  25  26  31  28  16  30  31  31  35  33  30  26  13  NA  30  28  29  NA  16  18  35  26  32  27  27  34  22  27
 [929]  NA  23  23  24  28  23  37  19  25  NA  23  38  NA  28  35  15  29  34  NA  27  35  22  38  45  NA  24  23  NA  38
 [958]  39  22  23  24  16  19  18  20  26  28  39  19  NA  34  25  26  32  NA  NA  18  NA  30  28  30  NA  29  46  21  22
 [987]  22 NaN  NA  22  21  NA  36  38  22   0  20  30  22  32
 [ reached getOption("max.print") -- omitted 1318 entries ]
Warning message:
NAs introduced by coercion
```
We can see that NA's are stored differently in this column. In this case they are found as NA or NaN. This is just this column, it is likely that other columns have other ways to specify NA.
To detect all the different ways in which an NA can be found I use the following command that gives you a list of all the potential ways in which an NA can be stored. Basically, this command:

- Scans all columns
- Converts values to character
- Trims whitespace
- Detects common “fake NA” representations
- Returns the unique suspicious values found
```R
different_ways_NAs <- unique(unlist(lapply(df, function(x) unique(x[grepl("^(na|nan|n/a|#n/a|#n/d|null|none|missing|nil|unknown|blank|\\s*)$", trimws(as.character(x)), ignore.case = TRUE)]))))
```
The following code automatically detects all potential fake NA's and transforms them as propeor NA's (empty space). I we run the original one liner code above, we will see that now it should be empty.
```R
df[] <- lapply(df, function(x) {
  x <- trimws(as.character(x))
  x[grepl("^(na|nan|n/a|#n/a|#n/d|#RIF!|null|none|missing|nil|unknown|blank|\\.*|-+|/+|_+|\\?+)?$", x, ignore.case = TRUE)] <- NA
  x
})
```
Now we can see the 'age' column for example and we will be able to speficy this column as a numeric without error:
```R
df$age <- as.numeric(df$age)
str(df)
```
In some cases the NA is stored as a '0'. Whether or not a zero is an NA needs to be checked with the person that created the dataframe.
### Some error in scoring
Now, we can take a look at the columns called *daily_usage_hours*. We can deduce that it should have numeric strings. However with the str(df) command, we can see that it is a chracter string. When we try to force the column to be numeric, we can see that there is an error, meaning that it has some *chr* strings somewhere.
We can take a look at the values of this column and how many times each value is found:
```R
table(df$daily_usage_hours)
```
From the results, we can see that there are some value sthat are not number, for example *I*, *l*, *o* and *O*. It is likely that the some of them are meant to be 1's and other are supposed to be 0's.
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
We can use the following code to find which ones are not number, in case one is skipping from us:
```R
unique(df$daily_usage_hours[!grepl("^[0-9]*\\.?[0-9]+$", trimws(as.character(df$daily_usage_hours)))])
```
Depending on the information of the dataframe, we could choose to convert all the incorrect entries as a NA.
```R
df$daily_usage_hours[
  !grepl("^[0-9]*\\.?[0-9]+$", trimws(as.character(df$daily_usage_hours)))
] <- NA
```
However, they may not be NA's. In this case I will convert the l and I to 1's and o and O to zeros.
```R
df$daily_usage_hours <- trimws(as.character(df$daily_usage_hours)) #Trim white spaces

df$daily_usage_hours[df$daily_usage_hours %in% c("I", "l")] <- "1"
df$daily_usage_hours[df$daily_usage_hours %in% c("o", "O")] <- "0"

df$daily_usage_hours <- as.numeric(df$daily_usage_hours)
```
But I can also do it for all the columns.
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
The uglification of the databse introduced many rows with NA's that probably should be eliminated. In the case of ther this dataframe, the solution on which rows to eliminate is quite easy. We cansee that the *user_id* is a assigned only once to each user (user_01 = USR00001; user_02 = USR00002; ...). Given that we have this information, we can eliminate all rows that have an NA or a zero in thos column.
```R
df <- filter(df, user_id != 0 ) %>%
  filter(user_id != " ")
```


