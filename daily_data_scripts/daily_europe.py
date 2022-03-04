import pandas as pd
import datetime
import sys
import sqlite3

sys.path.append("..")

from util import *

# JRC includes Italy data, but not the same subsets
def daily_italy():
    df_total = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_total.csv', error_bad_lines=False)
    df_region = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_region.csv', error_bad_lines=False)
    df_subregion = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_province.csv', error_bad_lines=False)

# Updates daily. Check for both the last two days' and today's data to make sure they are all gotten regardless of when the source is updated
def daily_ukraine():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()

    # get country_code for Ukraine
    ukraine_code = get_country_code("Ukraine", c)

    # get source id for Ukraine source
    ukraine_src_url = "https://github.com/dmytro-derkach/covid-19-ukraine"
    ukraine_src = get_source_id(ukraine_src_url, c)

    dt = datetime.datetime.today()
    ukraine_helper(get_date(dt), ukraine_code, ukraine_src, c, conn)

    for i in range(0, 2):
        dt -= datetime.timedelta(days=1)
        ukraine_helper(get_date(dt), ukraine_code, ukraine_src, c, conn)
    

def get_date(dt):
    return ('0' if dt.month < 10 else '')  + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day) + '-' + str(dt.year)


def ukraine_helper(date, ukraine_code, ukraine_src, c, conn):
    try:
        sql = '''SELECT date_collected FROM Cases_Per_Region WHERE date_collected = ?'''
        c.execute(sql, (date, ukraine_src))
        already_entered = True if c.fetchall() != [] else False
        if not already_entered:
            csv_name = 'https://raw.githubusercontent.com/dmytro-derkach/covid-19-ukraine/master/daily_reports/' + date + '.csv'
            df = pd.read_csv(csv_name, error_bad_lines=False)
            for row in df.itertuples():
                region_code = get_region_code(ukraine_code, row.Province_State, c)
                if region_code is None:
                    sql = '''INSERT INTO Regions (region_name, country_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
                    c.execute(sql,(row.Province_State, ukraine_code, row.Long_, row.Lat))
                    conn.commit()
                    region_code = get_region_code(ukraine_code, row.Province_State, c)
                sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(region_code, date, ukraine_src, row.Deaths_delta, row.Confirmed_delta, row.Recovered_delta))
            conn.commit()
    except:
        pass