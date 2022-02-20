import pandas as pd
import sqlite3
import datetime
from prototype_main_backend import *

# Use this for European countries only. Other countries appear to be either unreliable or have a lot of holes in their data.
def init_jrc():
    df = pd.read_csv('https://raw.githubusercontent.com/ec-jrc/COVID-19/master/data-by-region/jrc-covid-19-all-days-by-regions.csv', error_bad_lines=False)

# JRC includes Germany data, but not the same subsets
def init_germany():
    pass

# JRC includes UK data, but not the same subsets
def init_uk():
    pass

# JRC includes Italy data, but not the same subsets
def init_italy():
    df_total = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_total.csv', error_bad_lines=False)
    df_region = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_region.csv', error_bad_lines=False)
    df_subregion = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_province.csv', error_bad_lines=False)

# Starts on 03/03/2020.
def init_ukraine():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()

    # get country_code for Ukraine
    ukraine_code = get_country_code("Ukraine", c)
    print(ukraine_code)

    # insert and get source id for Ukraine source
    ukraine_src_url = "https://github.com/dmytro-derkach/covid-19-ukraine"
    set_source(ukraine_src_url, c, conn)
    ukraine_src = get_source_id(ukraine_src_url, c)
    print(ukraine_src)

    # set up regions for Ukraine; selected a random csv with all the regions
    random_csv = 'https://raw.githubusercontent.com/dmytro-derkach/covid-19-ukraine/master/daily_reports/03-03-2021.csv'
    df = pd.read_csv(random_csv, error_bad_lines=False)
    for row in df.itertuples():
      sql = '''INSERT INTO Regions (region_name, country_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
      c.execute(sql,(row.Province_State, ukraine_code, row.Long_, row.Lat))
    conn.commit()

    # Add data to Cases_Per_Region
    dt = datetime.datetime(2020, 3, 3)
    while (True):
        csv_name = 'https://raw.githubusercontent.com/dmytro-derkach/covid-19-ukraine/master/daily_reports/' + ('0' if dt.month < 10 else '')  + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day) + '-' + str(dt.year) + '.csv'
        print(csv_name)
        try:
            df = pd.read_csv(csv_name, error_bad_lines=False)
            for row in df.itertuples():
                sql = "SELECT region_code FROM Regions WHERE region_name = '" + row.Province_State + "' AND country_code = '" + ukraine_code + "';"
                c.execute(sql)
                region_code = c.fetchall()[0][0]
                sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(region_code, row.Last_Update, ukraine_src, row.Deaths_delta, row.Confirmed_delta, row.Recovered_delta))
            conn.commit()
        except:
            break
        dt += datetime.timedelta(days=1)

def init_france():
    pass

