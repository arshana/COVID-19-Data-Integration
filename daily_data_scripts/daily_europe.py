import pandas as pd
import datetime
import sys
import sqlite3
import json

sys.path.append("..")

from util import *

def daily_jrc():
    conn = sqlite3.connect('sqlite_db')
    c = conn.cursor()

    src_url = "https://github.com/ec-jrc/COVID-19"
    set_source(src_url, c, conn)
    src_id = get_source_id(src_url, c)

    daily_jrc_countries(src_id, c, conn)
    c.close()

# Use this for European countries only. Other countries appear to be either unreliable or have a lot of holes in their data.
# Using this in addition to JHU data, because it includes hospitalization data, while JHU does not
def daily_jrc_countries(src_id, c, conn):
    prev_death_dict = {}
    prev_recovered_dict = {}
    prev_cases_dict = {}

    i = 0
    with open('jrc_countries.json', 'r') as f:
        for line in f:
            if i == 0:
                prev_death_dict = json.loads(line)
            elif i == 1:
                prev_recovered_dict = json.loads(line)
            elif i == 2:
                prev_cases_dict = json.loads(line)
            i += 1
        f.close()

    missing_countries_set = set(())  # used to keep track of any countries that might need to be added to the countries table - for debugging purposes

    # Certain countries have strange data, regardless of if they are in the EU or not. This set has includes country names that don't seem to have that strange pattern.
    acceptable_countries_set = set(("Germany", "United Kingdom", "Italy", "Spain", "Romania", "Netherlands", "Belgium", "Sweden", "Austria", "Switzerland", "Slovakia", "Norway", "Albania"))  

    dt = datetime.datetime.today() - datetime.timedelta(days=2)
    for i in range(0, 3):
        date = jrc_date(dt)
        sql = '''SELECT date_collected FROM Cases_Per_Country WHERE date_collected = ? AND source_id = ?'''
        c.execute(sql, (date, src_id))
        already_entered = c.fetchall() != []
        if not already_entered:
            try:
                csv = "https://raw.githubusercontent.com/ec-jrc/COVID-19/master/data-by-country/jrc-covid-19-countries-" + date + ".csv"
                df = pd.read_csv(csv)
                for row in df.itertuples():
                    if row.EUcountry is True and row.CountryName in acceptable_countries_set:
                        country_code = get_country_code(row.CountryName, c)
                        
                        if country_code == None:
                            missing_countries_set.add(row.CountryName)

                        else:
                            sql = '''SELECT date_collected FROM Cases_Per_Country WHERE date_collected = ? AND source_id = ? AND country_code = ?'''
                            c.execute(sql, (row.Date, src_id, country_code))
                            already_entered = c.fetchall() != []
                            if not already_entered:
                                prev_death = 0 if country_code not in prev_death_dict else prev_death_dict[country_code]
                                prev_recovered = 0 if country_code not in prev_recovered_dict else prev_recovered_dict[country_code]
                                prev_cases = 0 if country_code not in prev_cases_dict else prev_cases_dict[country_code]

                                deaths = (row.CumulativeDeceased - prev_death) if isNum(row.CumulativeDeceased) else None
                                cases = (row.CumulativePositive - prev_cases) if isNum(row.CumulativePositive) else None
                                recovered = (row.CumulativeRecovered - prev_recovered) if isNum(row.CumulativeRecovered) else None
                                hospitalized = int(row.Hospitalized) if isNum(row.Hospitalized) else None
                                
                                sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers, hospitalization_numbers) VALUES (?, ?, ?, ?, ?, ?, ?)'''
                                c.execute(sql,(country_code, row.Date, src_id, deaths, cases, recovered, hospitalized))
                                
                                if isNum(row.CumulativeDeceased):
                                    prev_death_dict[country_code] = row.CumulativeDeceased
                                if isNum(row.CumulativeRecovered):
                                    prev_recovered_dict[country_code] = row.CumulativeRecovered
                                if isNum(row.CumulativePositive):
                                    prev_cases_dict[country_code] = row.CumulativePositive
                conn.commit()
            except:
                break
        dt += datetime.timedelta(days=1)

    # debugging
    #print(missing_countries_set)

    with open('jrc_countries.json', 'w') as f:
        f.write(json.dumps(prev_death_dict)+'\n')
        f.write(json.dumps(prev_recovered_dict)+'\n')
        f.write(json.dumps(prev_cases_dict)+'\n')
        f.close()


def jrc_date(dt):
    return str(dt.year) + ('0' if dt.month < 10 else '') + str(dt.month) + ('0' if dt.day < 10 else '') + str(dt.day)


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
            elif i == 2:
                prev_recovered_dict = json.loads(line)
            i += 1
        f.close()

    conn = sqlite3.connect('sqlite_db')
    c = conn.cursor()

    # get country_code
    italy_code = get_country_code("Italy", c)

    # get source id for source
    italy_src_url = "https://github.com/RamiKrispin/covid19italy"
    italy_src = get_source_id(italy_src_url, c)
    
    # insert total
    dt = datetime.datetime.today() - datetime.timedelta(days=2)
    for i in range(0, 3):
        date = get_italy_date(dt)
        sql = '''SELECT date_collected FROM Cases_Per_Country WHERE date_collected = ? AND source_id = ?'''
        c.execute(sql, (date, italy_src))
        already_entered = c.fetchall() != []
        if not already_entered:
            country_rows = df_total.loc[df_total['date'] == date]
            for i in range(len(country_rows)):
                row = country_rows.iloc[i]
                prev_death = 0 if "death" not in prev_row else prev_row["death"]
                prev_recovered = 0 if "recovered" not in prev_row else prev_row["recovered"]
                sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers, hospitalization_numbers) VALUES (?, ?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(italy_code, row.date, italy_src, (row.death - prev_death) if isNum(row.death) else None, int(row.daily_positive_cases) if isNum(row.daily_positive_cases) else None, (row.recovered - prev_recovered) if isNum(row.recovered) else None, int(row.total_hospitalized) if isNum(row.total_hospitalized) else None))
                if isNum(row.death):
                    prev_row["death"] = row.death
                if isNum(row.recovered):
                    prev_row["recovered"] = row.recovered
            conn.commit()
        dt += datetime.timedelta(days=1)
    
    # set up + insert regions
    dt = datetime.datetime.today() - datetime.timedelta(days=2)
    for i in range(0, 3):
        date = get_italy_date(dt)
        sql = '''SELECT date_collected FROM Cases_Per_Region WHERE date_collected = ? AND source_id = ?'''
        c.execute(sql, (date, italy_src))
        already_entered = c.fetchall() != []
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
                c.execute(sql,(region_code, row.date, italy_src, (row.death - prev_death) if isNum(row.death) else None, int(row.daily_positive_cases) if isNum(row.daily_positive_cases) else None, (row.recovered - prev_recovered) if isNum(row.recovered) else None, int(row.total_hospitalized) if isNum(row.total_hospitalized) else None))
                if isNum(row.death):
                    prev_death_dict[region_code] = row.death
                if isNum(row.recovered):
                    prev_recovered_dict[region_code] = row.recovered
            conn.commit()
        dt += datetime.timedelta(days=1)

    dt = datetime.datetime.today() - datetime.timedelta(days=2)
    italy_district_helper(get_italy_date(dt), italy_code, italy_src, df_subregion, c, conn)

    for i in range(0, 2):
        dt += datetime.timedelta(days=1)
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
    already_entered = c.fetchall() != []
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
    conn = sqlite3.connect('sqlite_db')
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
        already_entered = c.fetchall() != []
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