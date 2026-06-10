mkdir -p data
# need to test if this works
curl -o ./data/crime_data.csv "https://data.lacity.org/api/views/2nrs-mtv8/rows.csv?accessType=DOWNLOAD"