import pandas as pd

# Get country code associated with country_name from Countries table.
def get_country_code(country_name, c):
  c.execute('SELECT country_code FROM Countries WHERE country_name = "' + country_name + '"')
  result = c.fetchall()
  return result[0][0] if result != [] else None

# Get region code associated with region_name and country_code from Regions table.
def get_region_code(country_code, region_name, c):
  c.execute('SELECT region_code FROM Regions WHERE country_code = "' + country_code + '" AND region_name = "' + region_name + '"')
  result = c.fetchall()
  return result[0][0] if result != [] else None

# TODO Why does this insist on casting region_code to str?
# Get district code associated with district_name and region_code from Districts table.
def get_district_code(region_code, district_name, c):
  c.execute('SELECT district_code FROM Districts WHERE region_code = ' + str(region_code) + ' AND district_name = "' + district_name + '"')
  result = c.fetchall()
  return result[0][0] if result != [] else None

# Get source id associated with source_info from Sources table.
def get_source_id(source_info, c):
  c.execute("SELECT source_id FROM Sources WHERE source_information = '" + source_info + "'")
  result = c.fetchall()
  return result[0][0] if result != [] else None

# Insert a source into the Sources table if it is not already present
# source_info is typically a general url for the data source
def set_source(source_info, c, conn):
  src_id = get_source_id(source_info, c)
  if src_id is None:
    c.execute("INSERT INTO Sources (source_information) VALUES('" + source_info + "');")
    conn.commit()

# Check if a value is a number
def isNum(value):
  return (value is not None) and (not pd.isna(value)) and (str(value).lower() != "nan")