import pandas as pd 

# this functions takes in a csv file path and return a pandas dataframe
def crime_data_file_reader(file_path):
    pandas_dataframe = pd.read_csv(file_path)
    return pandas_dataframe