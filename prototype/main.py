import pandas as pd 
import numpy as np

def crime_data_file_reader(file_path):
    pandas_dataframe = pd.read_csv(file_path)
    return pandas_dataframe

df = crime_data_file_reader('data/crime_data.csv')

# ── Rename columns ────────────────────────────────────────────────────────────
df.rename(columns={
    'DR_NO'         : 'report_id',
    'Date Rptd'     : 'date_reported',
    'DATE OCC'      : 'date_occurred',
    'TIME OCC'      : 'time_occurred',
    'AREA'          : 'division_code',
    'AREA NAME'     : 'division_name',
    'Rpt Dist No'   : 'reporting_district',
    'LOCATION'      : 'address',
    'Cross Street'  : 'cross_street',
    'LAT'           : 'latitude',
    'LON'           : 'longitude',
    'Part 1-2'      : 'crime_severity',
    'Crm Cd'        : 'crime_code',
    'Crm Cd Desc'   : 'crime_description',
    'Crm Cd 1'      : 'crime_code_1',
    'Crm Cd 2'      : 'crime_code_2',
    'Crm Cd 3'      : 'crime_code_3',
    'Crm Cd 4'      : 'crime_code_4',
    'Mocodes'       : 'modus_operandi',
    'Vict Age'      : 'victim_age',
    'Vict Sex'      : 'victim_sex',
    'Vict Descent'  : 'victim_descent',
    'Premis Cd'     : 'premise_code',
    'Premis Desc'   : 'premise_description',
    'Weapon Used Cd': 'weapon_code',
    'Weapon Desc'   : 'weapon_description',
    'Status'        : 'status_code',
    'Status Desc'   : 'status_description',
}, inplace=True)

# ── Dates ─────────────────────────────────────────────────────────────────────
date_format = '%m/%d/%Y %I:%M:%S %p'
df['date_reported'] = pd.to_datetime(df['date_reported'], format=date_format).dt.normalize()
df['date_occurred'] = pd.to_datetime(df['date_occurred'], format=date_format).dt.normalize()
# FIX 1: added .dt.normalize() to strip the useless 12:00AM time from both columns

# ── Time occurred ─────────────────────────────────────────────────────────────
# FIX 2: removed the slow .dt.time conversion, use integer math instead
df['hour_occurred']   = (df['time_occurred'] // 100).astype('int8')
df['minute_occurred'] = (df['time_occurred'] % 100).astype('int8')
df.drop(columns=['time_occurred'], inplace=True)

# ── Coordinates ───────────────────────────────────────────────────────────────
# FIX 3: was using old column names 'LAT','LON' after renaming — now uses correct names
df.loc[(df['latitude'] == 0) & (df['longitude'] == 0), ['latitude', 'longitude']] = np.nan

# ── Victim age ────────────────────────────────────────────────────────────────
df['victim_age'] = df['victim_age'].replace(0, np.nan)
df.loc[df['victim_age'] < 0, 'victim_age'] = np.nan

# ── Victim sex ────────────────────────────────────────────────────────────────
valid_sex = ['M', 'F', 'X']
df['victim_sex'] = df['victim_sex'].where(df['victim_sex'].isin(valid_sex), np.nan)
# FIX 4: removed 'E' error flag — just use NaN, no need for a separate error value
# FIX 5: removed np.nan from valid_sex list — NaN is never equal to NaN so it
#         was being replaced by 'E' anyway, causing existing NaNs to become 'E'

# ── Victim descent ────────────────────────────────────────────────────────────
descent_map = {
    'H': 'Hispanic',       'W': 'White',
    'B': 'Black',          'A': 'Asian',
    'C': 'Chinese',        'J': 'Japanese',
    'K': 'Korean',         'V': 'Vietnamese',
    'F': 'Filipino',       'I': 'American Indian',
    'Z': 'Asian Indian',   'L': 'Laotian',
    'G': 'Guamanian',      'P': 'Pacific Islander',
    'D': 'Cambodian',      'U': 'Hawaiian',
    'S': 'Samoan',         'O': 'Other',
    'X': 'Unknown',        '-': 'Unknown'
}
df['victim_descent'] = df['victim_descent'].map(descent_map)

# ── Weapon / MO / cross street ────────────────────────────────────────────────
df['weapon_code']        = df['weapon_code'].fillna(0).astype(int)
df['weapon_description'] = df['weapon_description'].fillna('No Weapon')
df['modus_operandi']     = df['modus_operandi'].fillna('')
df['cross_street']       = df['cross_street'].fillna('')

# ── Drop unused columns ───────────────────────────────────────────────────────
# FIX 6: removed 'LAT','LON' from drop list — they were already renamed to
#         latitude/longitude so dropping 'LAT','LON' would throw a KeyError
df.drop(columns=['crime_code_2', 'crime_code_3', 'crime_code_4'], inplace=True)

print(df.info())