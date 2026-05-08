# Convert flat dataframe to relational
Sometimes relational databases are better to store big amount of data. Transforming a 'flat' dataframe is relatively easy, it requieres to know the database to understand which columns can be agregated into a relational tables and which 'id' we will use as a *primary key* and which ones as *foreign keys*.
For this I have developed an all purpose [python script](https://github.com/EmilianoMora/data_cleaning/blob/main/relational_database/flat_table_to_relational.py) that uses a CSV dataframe as input and generates a relational database as output. The usage of the script is as follows:
```
python flat_table_to_relational.py /PATH/TO/INPUT/social_media_user_behavior.csv /PATH/TO/OUTPUT/social_media_user_behavior.db
```
