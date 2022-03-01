def get_country_code(country_name, c):
  c.execute("SELECT country_code FROM Countries WHERE country_name = '" + country_name + "'")
  result = c.fetchall()
  return result[0][0]

def get_region_code(country_code, region_name, c):
  c.execute('SELECT region_code FROM Regions WHERE country_code = "' + country_code + '" AND region_name = "' + region_name + '"')
  result = c.fetchall()
  return result[0][0] if result != [] else None

# TODO Why does this insist on casting region_code to str
def get_district_code(region_code, district_name, c):
  c.execute('SELECT district_code FROM Districts WHERE region_code = "' + str(region_code) + '" AND district_name = "' + district_name + '"')
  result = c.fetchall()
  return result[0][0]

# source_info is typically a general url for the data source
def set_source(source_info, c, conn):
  c.execute("INSERT INTO Sources (source_information) VALUES('" + source_info + "');")
  conn.commit()

def get_source_id(source_info, c):
  c.execute("SELECT source_id FROM Sources WHERE source_information = '" + source_info + "'")
  result = c.fetchall()
  return result[0][0]