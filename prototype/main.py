#this where to do the work
import pandas as pd 
import numpy as np

# this functions takes in a csv file path and return a pandas dataframe
def crime_data_file_reader(file_path):
    pandas_dataframe = pd.read_csv(file_path)
    return pandas_dataframe

df = crime_data_file_reader('data/crime_data.csv')

# checking the first five rows
# print(df.head())

#how to see the columns in pandas dataframe
# print(df.info())

# first lets rename the columns
df.rename(columns={
    # Identifiers & Report Info
    'DR_NO'         : 'report_id',
    'Date Rptd'     : 'date_reported',
    'DATE OCC'      : 'date_occurred',
    'TIME OCC'      : 'time_occurred',

    # Geographic / Division
    'AREA'          : 'division_code',
    'AREA NAME'     : 'division_name',
    'Rpt Dist No'   : 'reporting_district',
    'LOCATION'      : 'address',
    'Cross Street'  : 'cross_street',
    'LAT'           : 'latitude',
    'LON'           : 'longitude',

    # Crime Classification
    'Part 1-2'      : 'crime_severity',        # 1 = serious, 2 = less serious
    'Crm Cd'        : 'crime_code',
    'Crm Cd Desc'   : 'crime_description',
    'Crm Cd 1'      : 'crime_code_1',
    'Crm Cd 2'      : 'crime_code_2',
    'Crm Cd 3'      : 'crime_code_3',
    'Crm Cd 4'      : 'crime_code_4',
    'Mocodes'       : 'modus_operandi',

    # Victim Info
    'Vict Age'      : 'victim_age',
    'Vict Sex'      : 'victim_sex',
    'Vict Descent'  : 'victim_descent',

    # Premise & Weapon
    'Premis Cd'     : 'premise_code',
    'Premis Desc'   : 'premise_description',
    'Weapon Used Cd': 'weapon_code',
    'Weapon Desc'   : 'weapon_description',

    # Case Status
    'Status'        : 'status_code',
    'Status Desc'   : 'status_description',
}, inplace=True)

# to check the column have been renamed
# print(df.columns.tolist())

# lets check the change the datetime date reported, occurred 
# date reported &&&&&&&&
# Check if ALL time portions are midnight
# date_format = '%m/%d/%Y %I:%M:%S %p'

# df['date_reported'] = pd.to_datetime(df['date_reported'], format=date_format)

# # Check if all times are midnight (12:00:00 AM)
# all_midnight = (df['date_reported'].dt.hour == 0) & \
#                (df['date_reported'].dt.minute == 0) & \
#                (df['date_reported'].dt.second == 0)

# print(all_midnight.all())   # True = every row is midnight, safe to drop time

# # Also useful — see how many are NOT midnight
# print(f"Non-midnight rows: {(~all_midnight).sum()}")

#this is the way to clean the date reported
#skipped the time as all of them were 12am 
date_format = '%m/%d/%Y %I:%M:%S %p'
df['date_reported'] = pd.to_datetime(df['date_reported'],format=date_format)

# checking if only the date occurred
# print(df['date_reported'].head())

# date_occurred &&&&
#skipped the time as all of them were 12am 

df['date_occurred'] = pd.to_datetime(df['date_occurred'],format=date_format)
# print(df['date_occurred'].head())


# time_occurred &&&&&

# convert to proper time
# Instead of converting to time object, just extract hour and minute as integers
# making this into a time takes soo damn long
# performance issues
df['time_occurred'] = pd.to_datetime(
    df['time_occurred'].astype(str).str.zfill(4), 
    format='%H%M'
).dt.time

# verify
# print(df['time_occurred'].head(30))

#division_code and division_name does not need it

# reporting district &&&&&&
# print(df[['reporting_district']].drop_duplicates())

#latitude and longitude
missing_coords = ((df['latitude'] == 0) & (df['longitude'] == 0)).sum()
print(f"Missing coordinates (0,0): {missing_coords}")
print(f"Percentage: {missing_coords / len(df) * 100:.2f}%")
df.loc[(df['latitude'] == 0) & (df['longitude'] == 0), ['LAT', 'LON']] = np.nan




