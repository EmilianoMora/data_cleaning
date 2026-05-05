# data_cleaning
This repository is aimed store basic data cleaning scripts (mostly for me)

Through many years of doing data analyses for my masters, PhD and posdoc, I have developed many scripts to help me check the quality of my data. However, these scripts ad the knowledge within them are usually scatered in many different files. This repository is aimed at putting it in all together to keep track of them. 

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
In order to introduce messyness into the dataset, I used [*Ugly CSV generator*](https://github.com/LucaCappelletti94/ugly_csv_generator) which is a python package that introduces automated non-destructive errors.

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
