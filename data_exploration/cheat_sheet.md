# Cheat sheet pandas and R commands
Here is a cheat sheet of the most common commands for data management in both pandas (python) and R.

| **Purpose**                      | **Pandas Function**  | **Pandas Example**                           | **R Equivalent**                | **R Example**                       |
| -------------------------------- | -------------------- | -------------------------------------------- | ------------------------------- | ----------------------------------- |
| Read CSV file                    | pd.read_csv()        | df = pd.read_csv("data.csv")                 | read.csv()                      | df <- read.csv("data.csv")          |
| Show first rows                  | df.head()            | df.head()                                    | head()                          | head(df)                            |
| Show last rows                   | df.tail()            | df.tail()                                    | tail()                          | tail(df)                            |
| Display structure and data types | df.info()            | df.info()                                    | str()                           | str(df)                             |
| Summary statistics               | df.describe()        | df.describe()                                | summary()                       | summary(df)                         |
| Get rows and columns             | df.shape             | df.shape                                     | dim()                           | dim(df)                             |
| List column names                | df.columns           | df.columns                                   | colnames()                      | colnames(df)                        |
| Show data types                  | df.dtypes            | df.dtypes                                    | sapply(df, class)               | sapply(df, class)                   |
| Select one column                | df["col"]            | df["age"]                                    | $ or []                         | df$age                              |
| Select multiple columns          | df[["a","b"]]        | df[["name","age"]]                           | subset columns                  | df[, c("name","age")]               |
| Select row by position           | df.iloc[0]           | df.iloc[0]                                   | indexing                        | df[1, ]                             |
| Select row by label              | df.loc[0]            | df.loc[0]                                    | indexing                        | df[1, ]                             |
| Sort rows                        | df.sort_values()     | df.sort_values("age")                        | order()                         | df[order(df$age), ]                 |
| Group data                       | df.groupby()         | df.groupby("dept")["salary"].mean()          | aggregate() / dplyr::group_by() | aggregate(salary ~ dept, df, mean)  |
| Average                          | df.mean()            | df["salary"].mean()                          | mean()                          | mean(df$salary)                     |
| Sum values                       | df.sum()             | df["sales"].sum()                            | sum()                           | sum(df$sales)                       |
| Minimum value                    | df.min()             | df["age"].min()                              | min()                           | min(df$age)                         |
| Maximum value                    | df.max()             | df["age"].max()                              | max()                           | max(df$age)                         |
| Count non-null values            | df.count()           | df.count()                                   | length() / sum(!is.na())        | sum(!is.na(df$age))                 |
| Detect missing values            | df.isnull()          | df.isnull()                                  | is.na()                         | is.na(df)                           |
| Remove missing values            | df.dropna()          | df.dropna()                                  | na.omit()                       | na.omit(df)                         |
| Replace missing values           | df.fillna()          | df.fillna(0)                                 | replace NA                      | df[is.na(df)] <- 0                  |
| Rename columns                   | df.rename()          | df.rename(columns={"a":"A"})                 | colnames()                      | colnames(df)[1] <- "A"              |
| Remove rows/columns              | df.drop()            | df.drop(columns=["age"])                     | NULL assignment                 | df$age <- NULL                      |
| Join tables                      | df.merge()           | pd.merge(df1, df2, on="id")                  | merge()                         | merge(df1, df2, by="id")            |
| Combine tables                   | df.concat()          | pd.concat([df1, df2])                        | rbind() / cbind()               | rbind(df1, df2)                     |
| Unique values                    | df.unique()          | df["city"].unique()                          | unique()                        | unique(df$city)                     |
| Frequency counts                 | df.value_counts()    | df["city"].value_counts()                    | table()                         | table(df$city)                      |
| Filter rows                      | df.query()           | df.query("age > 30")                         | subset()                        | subset(df, age > 30)                |
| Apply function                   | df.apply()           | df["x"].apply(np.sqrt)                       | sapply()                        | sapply(df$x, sqrt)                  |
| Change data type                 | df.astype()          | df["age"].astype(int)                        | as.integer()                    | as.integer(df$age)                  |
| Write CSV file                   | df.to_csv()          | df.to_csv("out.csv")                         | write.csv()                     | write.csv(df, "out.csv")            |
| Create dataframe                 | pd.DataFrame()       | pd.DataFrame(data)                           | data.frame()                    | data.frame(data)                    |
| Random sample rows               | df.sample()          | df.sample(5)                                 | sample()                        | df[sample(nrow(df),5), ]            |
| Create pivot table               | df.pivot_table()     | df.pivot_table(values="sales", index="dept") | xtabs() / pivot_wider()         | xtabs(sales ~ dept, df)             |
| Find duplicates                  | df.duplicated()      | df.duplicated()                              | duplicated()                    | duplicated(df)                      |
| Remove duplicates                | df.drop_duplicates() | df.drop_duplicates()                         | unique()                        | unique(df)                          |
| Reset row index                  | df.reset_index()     | df.reset_index()                             | rownames <- NULL                | rownames(df) <- NULL                |
| Set index column                 | df.set_index()       | df.set_index("id")                           | rownames()                      | rownames(df) <- df$id               |
| Correlation matrix               | df.corr()            | df.corr()                                    | cor()                           | cor(df)                             |
| Plot data                        | df.plot()            | df.plot()                                    | plot()                          | plot(df$x, df$y)                    |
| Convert to NumPy array           | df.to_numpy()        | df.to_numpy()                                | as.matrix()                     | as.matrix(df)                       |
| First column by position         | df.iloc[:,0]         | df.iloc[:,0]                                 | indexing                        | df[,1]                              |
| Conditional filtering            | df.loc[df["x"]>5]    | df.loc[df["x"] > 5]                          | subset()                        | subset(df, x > 5)                   |
| Count unique values              | df.nunique()         | df["city"].nunique()                         | length(unique())                | length(unique(df$city))             |
| Memory usage                     | df.memory_usage()    | df.memory_usage()                            | object.size()                   | object.size(df)                     |
| Sort by index                    | df.sort_index()      | df.sort_index()                              | order(rownames())               | df[order(rownames(df)), ]           |
| Transpose dataframe              | df.transpose()       | df.transpose()                               | t()                             | t(df)                               |
| Replace values                   | df.replace()         | df.replace("M","Male")                       | gsub() / indexing               | df$gender[df$gender=="M"] <- "Male" |
