import pandas as pd
import sqlite3
import datetime
import sys

sys.path.append("..")

from util import *

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
        if get_region_code(italy_code, region_row.region_name, c) is None:
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
        if get_district_code(region_code, subregion_row.province_name, c) is None:
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

# Starts on 03/03/2020.
def init_ukraine():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()

    # get country_code for Ukraine
    ukraine_code = get_country_code("Ukraine", c)

    # insert and get source id for Ukraine source
    ukraine_src_url = "https://github.com/dmytro-derkach/covid-19-ukraine"
    set_source(ukraine_src_url, c, conn)
    ukraine_src = get_source_id(ukraine_src_url, c)

    # set up regions for Ukraine; selected a random csv with all the regions
    random_csv = 'https://raw.githubusercontent.com/dmytro-derkach/covid-19-ukraine/master/daily_reports/03-03-2021.csv'
    df = pd.read_csv(random_csv, error_bad_lines=False)
    for row in df.itertuples():
        if get_region_code(ukraine_code, row.Province_State, c) is None:
            sql = '''INSERT INTO Regions (region_name, country_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
            c.execute(sql,(row.Province_State, ukraine_code, row.Long_, row.Lat))
            conn.commit()

    # Add data to Cases_Per_Region
    dt = datetime.datetime(2020, 3, 3)
    while (True):
        date = ('0' if dt.month < 10 else '')  + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day) + '-' + str(dt.year)
        csv_name = 'https://raw.githubusercontent.com/dmytro-derkach/covid-19-ukraine/master/daily_reports/' + date + '.csv'
        try:
            df = pd.read_csv(csv_name, error_bad_lines=False)
            for row in df.itertuples():
                sql = "SELECT region_code FROM Regions WHERE region_name = '" + row.Province_State + "' AND country_code = '" + ukraine_code + "';"
                c.execute(sql)
                region_code = c.fetchall()[0][0]
                sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(region_code, date, ukraine_src, row.Deaths_delta, row.Confirmed_delta, row.Recovered_delta))
            conn.commit()
        except:
            break
        dt += datetime.timedelta(days=1)
    
    conn.close()

def init_france():
    pass
