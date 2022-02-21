import sqlite3
import pandas as pd

def get_country_code(country_name, c):
  c.execute("SELECT country_code FROM Countries WHERE country_name = '" + country_name + "'")
  result = c.fetchall()
  return result[0][0]

def get_region_code(country_code, region_name, c):
  c.execute('SELECT region_code FROM Regions WHERE country_code = "' + country_code + '" AND region_name = "' + region_name + '"')
  result = c.fetchall()
  return result[0][0]

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

conn = sqlite3.connect('prototype_db')
c = conn.cursor()

c.execute('''
            CREATE TABLE Countries(
            country_code VARCHAR(2) PRIMARY KEY,
            country_name VARCHAR(128) UNIQUE NOT NULL
            )
          ''')
c.execute('''
            CREATE TABLE Regions(
            region_code INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            region_name VARCHAR(128) NOT NULL,
            country_code VARCHAR(2) NOT NULL,
            longitude FLOAT NULL,
            latitude FLOAT NULL,
            FOREIGN KEY (country_code) REFERENCES Countries(country_code)
            )
          ''')

c.execute('''
            CREATE TABLE Districts(
                district_code INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                district_name VARCHAR(128) NOT NULL,
                region_code BIGINT NOT NULL,
                longitude FLOAT NULL,
                latitude FLOAT NULL,
                FOREIGN KEY (region_code) REFERENCES Regions(region_code)
            )
          ''')

c.execute('''
            CREATE TABLE Sources(
                source_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                source_information VARCHAR(256) UNIQUE NOT NULL
            )
          ''')

c.execute('''
            CREATE TABLE Cases_Per_Country(
                country_code VARCHAR(2) ,
                date_collected DATETIME2 NOT NULL,
                source_id BIGINT NOT NULL,
                death_numbers INT NULL,
                case_numbers INT NULL,
                recovery_numbers INT NULL,
                hospitalization_numbers INT NULL,
                FOREIGN KEY (country_code) REFERENCES Countries(country_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Cases_Per_Region(
                region_code BIGINT,
                date_collected DATETIME2 NOT NULL,
                source_id BIGINT NOT NULL,
                death_numbers INT NULL,
                case_numbers INT NULL,
                recovery_numbers INT NULL,
                hospitalization_numbers INT NULL,
                FOREIGN KEY (region_code) REFERENCES Regions(region_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Cases_Per_District(
                district_code BIGINT,
                date_collected DATETIME2 NOT NULL,
                source_id BIGINT NOT NULL,
                death_numbers INT NULL,
                case_numbers INT NULL,
                recovery_numbers INT NULL,
                hospitalization_numbers INT NULL,
                FOREIGN KEY (district_code) REFERENCES Districts(district_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_Country(
                vaccination_rate FLOAT NOT NULL,
                country_code VARCHAR(2) PRIMARY KEY,
                source_id BIGINT NOT NULL,
                FOREIGN KEY (country_code) REFERENCES Countries(country_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_Region(
                vaccination_rate FLOAT NOT NULL,
                region_code BIGINT PRIMARY KEY,
                source_id BIGINT NOT NULL,
                FOREIGN KEY (region_code) REFERENCES Regions(region_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_District(
                vaccination_rate FLOAT NOT NULL,
                district_code BIGINT PRIMARY KEY,
                source_id BIGINT NOT NULL,
                FOREIGN KEY (district_code) REFERENCES Districts(district_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''CREATE TABLE Population_Per_Country(
            country_code VARCHAR(2) PRIMARY KEY,
            population_amount BIGINT NOT NULL,
            date_collected DATETIME2 NOT NULL,
            FOREIGN KEY (country_code) REFERENCES Countries(country_code)
        ); 
        ''')

c.execute('''CREATE TABLE Population_Per_Region(
            region_code BIGINT PRIMARY KEY,
            population_amount BIGINT NOT NULL,
            date_collected DATETIME2 NOT NULL,
            FOREIGN KEY (region_code) REFERENCES Regions(region_code)
        );
         ''')

c.execute('''CREATE TABLE Population_Per_District(
            district_code BIGINT PRIMARY KEY,
            population_amount BIGINT NOT NULL,
            date_collected DATETIME2 NOT NULL,
            FOREIGN KEY (district_code) REFERENCES Districts(district_code)
        ); 
        ''')
                  
conn.commit()

#insert country_countryCode table
countries = pd.read_csv('country_countryCode.csv')
countries = countries.rename(columns={"Name": "country_name", "Code": "country_code"})
countries.to_sql('Countries',con=conn, if_exists = 'append', index=False)

c.close()

def init_italy():
    df_total = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_total.csv', error_bad_lines=False)
    df_region = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_region.csv', error_bad_lines=False)
    df_subregion = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_province.csv', error_bad_lines=False)

    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()

    # get country_code
    italy_code = get_country_code("Italy", c)

    # insert and get source id for source
    italy_src_url = "https://github.com/RamiKrispin/covid19italy"
    set_source(italy_src_url, c, conn)
    italy_src = get_source_id(italy_src_url, c)

    # insert total
    prev_row = None
    for row in df_total.itertuples():
        prev_death = 0 if prev_row is None else prev_row.death
        prev_recovered = 0 if prev_row is None else prev_row.recovered
        sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers, hospitalization_numbers) VALUES (?, ?, ?, ?, ?, ?, ?)'''
        c.execute(sql,(italy_code, row.date, italy_src, row.death - prev_death if row.death is not "NaN" else None, int(row.daily_positive_cases) if row.daily_positive_cases is not "NaN" else None, row.recovered - prev_recovered if row.recovered is not "NaN" else None, int(row.total_hospitalized) if row.total_hospitalized is not "NaN" else None))
        prev_row = row
    conn.commit()

    # set up regions
    src_region_codes = df_region["region_code"].unique()
    for src_code in src_region_codes:
        region_rows = df_region.loc[df_region['region_code'] == src_code]
        region_row = region_rows.iloc[0]
        sql = '''INSERT INTO Regions (region_name, country_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
        c.execute(sql,(region_row.region_name, italy_code, region_row.long, region_row.lat))
    conn.commit()
    
    # insert regions
    region_code = get_region_code(italy_code, region_row.region_name, c)
    prev_death_dict = {}
    prev_recovered_dict = {}
    for row in df_region.itertuples():
        region_code = get_region_code(italy_code, row.region_name, c)
        prev_death = 0 if region_code not in prev_death_dict else prev_death_dict[region_code]
        prev_recovered = 0 if region_code not in prev_recovered_dict else prev_recovered_dict[region_code]
        sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers, hospitalization_numbers) VALUES (?, ?, ?, ?, ?, ?, ?)'''
        c.execute(sql,(region_code, row.date, italy_src, row.death - prev_death if row.death is not "NaN" else None, int(row.daily_positive_cases) if row.daily_positive_cases is not "NaN" else None, row.recovered - prev_recovered if row.recovered is not "NaN" else None, int(row.total_hospitalized) if row.total_hospitalized is not "NaN" else None))
        if row.death is not "NaN":
            prev_death_dict[region_code] = row.death
        if row.recovered is not "NaN":
            prev_recovered_dict[region_code] = row.recovered
    conn.commit()

    # set up + insert subregion
    src_subregion_codes = df_subregion["province_code"].unique()
    for src_code in src_subregion_codes:
        subregion_rows = df_subregion.loc[df_subregion['province_code'] == src_code]
        subregion_row = subregion_rows.iloc[0]
        region_code = get_region_code(italy_code, subregion_row.region_name, c)
        sql = '''INSERT INTO Districts (district_name, region_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
        c.execute(sql,(subregion_row.province_name, region_code, subregion_row.long, subregion_row.lat))
        conn.commit()
        subregion_code = get_district_code(region_code, subregion_row.province_name, c)
        for i in range(len(subregion_rows)):
            row = subregion_rows.iloc[i]
            sql = '''INSERT INTO Cases_Per_District (district_code, date_collected, source_id, case_numbers) VALUES (?, ?, ?, ?)'''
            c.execute(sql,(subregion_code, row.date, italy_src, int(row.new_cases)))
        conn.commit()

    conn.close()