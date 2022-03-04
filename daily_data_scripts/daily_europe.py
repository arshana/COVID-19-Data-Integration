import pandas as pd
import datetime
import sys
import sqlite3
import json

sys.path.append("..")

from util import *

# JRC includes Italy data, but not the same subsets
def daily_italy():
    df_total = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_total.csv', error_bad_lines=False)
    df_region = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_region.csv', error_bad_lines=False)
    df_subregion = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_province.csv', error_bad_lines=False)

    i = 0
    prev_row = {}
    prev_death_dict = {}
    prev_recovered_dict = {}
    with open('italy.json', 'r') as f:
        for line in f:
            if i == 0:
                prev_row = json.loads(line)
            elif i == 1:
                prev_death_dict = json.loads(line)
            if i == 2:
                prev_recovered_dict = json.loads(line)
            i += 1
        f.close()

    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()

    # get country_code
    italy_code = get_country_code("Italy", c)

    # get source id for source
    italy_src_url = "https://github.com/RamiKrispin/covid19italy"
    italy_src = get_source_id(italy_src_url, c)
    
    # insert total
    dt = datetime.datetime.today()
    for i in range(0, 3):
        date = get_italy_date(dt)
        sql = '''SELECT date_collected FROM Cases_Per_Country WHERE date_collected = ? AND source_id = ?'''
        c.execute(sql, (date, italy_src))
        already_entered = c.fetchall() == []
        if not already_entered:
            country_rows = df_total.loc[df_total['date'] == date]
            for i in range(len(country_rows)):
                row = country_rows.iloc[i]
                prev_death = 0 if "death" not in prev_row else prev_row["death"]
                prev_recovered = 0 if "recovered" not in prev_row else prev_row["recovered"]
                sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers, hospitalization_numbers) VALUES (?, ?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(italy_code, row.date, italy_src, row.death - prev_death if row.death is not "NaN" else None, int(row.daily_positive_cases) if row.daily_positive_cases is not "NaN" else None, row.recovered - prev_recovered if row.recovered is not "NaN" else None, int(row.total_hospitalized) if row.total_hospitalized is not "NaN" else None))
                if row.death is not "NaN":
                    prev_row["death"] = row.death
                if row.recovered is not "NaN":
                    prev_row["recovered"] = row.recovered
            conn.commit()
        dt -= datetime.timedelta(days=1)
    
    # set up + insert regions
    dt = datetime.datetime.today()
    for i in range(0, 3):
        date = get_italy_date(dt)
        sql = '''SELECT date_collected FROM Cases_Per_Region WHERE date_collected = ? AND source_id = ?'''
        c.execute(sql, (date, italy_src))
        already_entered = c.fetchall() == []
        if not already_entered:
            region_rows = df_region.loc[df_region['date'] == date]
            for i in range(len(region_rows)):
                row = region_rows.iloc[i]
                region_code = get_region_code(italy_code, row.region_name, c)
                if region_code is None:
                    sql = '''INSERT INTO Regions (region_name, country_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
                    c.execute(sql,(row.region_name, italy_code, row.long, row.lat))
                    conn.commit()
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
        dt -= datetime.timedelta(days=1)

    dt = datetime.datetime.today()
    italy_district_helper(get_italy_date(dt), italy_code, italy_src, df_subregion, c, conn)

    for i in range(0, 2):
        dt -= datetime.timedelta(days=1)
        italy_district_helper(get_italy_date(dt), italy_code, italy_src, df_subregion, c, conn)
            
    conn.close()

    with open('italy.json', 'w') as f:
        f.write(json.dumps(prev_row)+'\n')
        f.write(json.dumps(prev_death_dict)+'\n')
        f.write(json.dumps(prev_recovered_dict)+'\n')
        f.close()


def get_italy_date(dt):
    return str(dt.year)+ '-' + ('0' if dt.month < 10 else '') + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day)


def italy_district_helper(date, italy_code, italy_src, df_subregion, c, conn):
    sql = '''SELECT date_collected FROM Cases_Per_District WHERE date_collected = ? AND source_id = ?'''
    c.execute(sql, (date, italy_src))
    already_entered = c.fetchall() == []
    if not already_entered:
        subregion_rows = df_subregion.loc[df_subregion['date'] == date]
        for i in range(len(subregion_rows)):
            row = subregion_rows.iloc[i]
            region_code = get_region_code(italy_code, row.region_name, c)
            if region_code is None:
                sql = '''INSERT INTO Regions (region_name, country_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
                c.execute(sql,(row.region_name, italy_code, row.long, row.lat))
                conn.commit()
                region_code = get_region_code(italy_code, row.region_name, c)
            subregion_code = get_district_code(region_code, row.province_name, c)
            if subregion_code is None:
                sql = '''INSERT INTO Districts (district_name, region_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
                c.execute(sql,(row.province_name, region_code, row.long, row.lat))
                conn.commit()
                subregion_code = get_district_code(region_code, row.province_name, c)
            sql = '''INSERT INTO Cases_Per_District (district_code, date_collected, source_id, case_numbers) VALUES (?, ?, ?, ?)'''
            c.execute(sql,(subregion_code, row.date, italy_src, int(row.new_cases)))
        conn.commit()


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
    ukraine_helper(get_ukraine_date(dt), ukraine_code, ukraine_src, c, conn)

    for i in range(0, 2):
        dt -= datetime.timedelta(days=1)
        ukraine_helper(get_ukraine_date(dt), ukraine_code, ukraine_src, c, conn)
    

def get_ukraine_date(dt):
    return ('0' if dt.month < 10 else '')  + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day) + '-' + str(dt.year)


def ukraine_helper(date, ukraine_code, ukraine_src, c, conn):
    try:
        sql = '''SELECT date_collected FROM Cases_Per_Region WHERE date_collected = ? AND source_id = ?'''
        c.execute(sql, (date, ukraine_src))
        already_entered = c.fetchall() == []
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