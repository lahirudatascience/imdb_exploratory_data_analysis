def load_data(file_path):
    import pandas as pd
    return pd.read_csv(file_path)

def calculate_descriptive_statistics(df):
    return df.describe()

def investigate_trends(df, column, time_column):
    return df.groupby(time_column)[column].mean()

def find_outliers(df, column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return df[(df[column] < lower_bound) | (df[column] > upper_bound)]