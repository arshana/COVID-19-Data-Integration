import pandas as pd
import sqlite3
import datetime

from util import *

def init_jhu():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()

    # insert and get source id for source
    src_url = "https://github.com/CSSEGISandData/COVID-19"
    set_source(src_url, c, conn)
    src_id = get_source_id(src_url, c)
    
    init_jhu_us_states(c, conn, src_id)
    init_jhu_global(c, conn, src_id)

    conn.close()

# US States from JHU data
# ONLY SAFE TO CALL FROM init_jhu in this state (otherwise consider that source may be replicated, etc.)
# First csv: 04-12-2020
def init_jhu_us_states(c, conn, src_id):
    # get country_code
    us_code = get_country_code("United States", c)    
    
    # intentionally selected this csv compared to some of the others to avoid the so-called Recovered region
    setup_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/05-09-2021.csv")

    # insert US states in Regions
    for row in setup_df.itertuples():
        region_name = row.Province_State
        if get_region_code(us_code, region_name, c) is None:
            sql = '''INSERT INTO Regions (region_name, country_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
            c.execute(sql,(region_name, us_code, row.Long_, row.Lat))
    conn.commit()

    # insert state data in Cases_per_Region
    # the data is cumulative - need the previous data to accurately update the new data
    dt = datetime.datetime(2020, 4, 12)
    last_error = ""
    prev_death_dict = {}
    prev_recovered_dict = {}
    prev_case_dict = {}
    prev_hospitalized_dict = {}
    while (True):
        date = ('0' if dt.month < 10 else '')  + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day) + '-' + str(dt.year)
        csv_name = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/' + date + '.csv'
        try:
            df = pd.read_csv(csv_name, error_bad_lines=False)
            for row in df.itertuples():
                region_code = get_region_code(us_code, row.Province_State, c)
                prev_death = 0 if region_code not in prev_death_dict else prev_death_dict[region_code]
                prev_recovered = 0 if region_code not in prev_recovered_dict else prev_recovered_dict[region_code]
                prev_case = 0 if region_code not in prev_case_dict else prev_case_dict[region_code]
                prev_hospitalized = 0 if region_code not in prev_hospitalized_dict else prev_hospitalized_dict[region_code]
                if region_code is not None:
                    sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers, hospitalization_numbers) VALUES (?, ?, ?, ?, ?, ?, ?)'''
                    # handles the case of a blank column by inserting None
                    c.execute(sql,(region_code, date, src_id, row.Deaths - prev_death if row.Deaths is not None else None, row.Confirmed - prev_case if row.Confirmed is not None else None, row.Recovered - prev_recovered if row.Recovered is not None else None, row.People_Hospitalized - prev_hospitalized if row.People_Hospitalized is not None else None))
                    # update previous
                    if row.Deaths is not None:
                        prev_death_dict[region_code] = row.Deaths
                    if row.Recovered is not None:
                        prev_recovered_dict[region_code] = row.Recovered
                    if row.Confirmed is not None:
                        prev_case_dict[region_code] = row.Confirmed
                    if row.People_Hospitalized is not None:
                        prev_hospitalized_dict[region_code] = row.People_Hospitalized
                else:
                    last_error = (row.Province_State + " was missing from the Regions table - init_jhu_us_states " + csv_name + ".")
            conn.commit()
        except:
            break
        dt += datetime.timedelta(days=1)

    print(last_error)

# Global JHU data
# ONLY SAFE TO CALL FROM init_jhu in this state (otherwise consider that source may be replicated, etc.)
# First csv: 01-22-2020
def init_jhu_global(c, conn, src_id):
    dt = datetime.datetime(2020, 1, 22)
    missing_countries_set = {}  # used to keep track of any countries that might need to be added to the countries table - for debugging purposes
    
    # can be used for country and region codes since they are unique from each other
    prev_death_dict = {}
    prev_recovered_dict = {}
    prev_case_dict = {}

    # TODO test again after the Namibia issue from prototype_main_backend is fixed
    while (True):
        date = ('0' if dt.month < 10 else '')  + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day) + '-' + str(dt.year)
        csv_name = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + date + '.csv'
        try:
            df = pd.read_csv(csv_name, error_bad_lines=False)
            for row in df.itertuples():
                # normalize country name
                country_name = row.Country_Region
                if (country_name == "Burma"):
                    country_name = "Myanmar"
                elif (country_name == "Czechia"):
                    country_name = "Czech Republic"
                elif (country_name == "Taiwan*"):
                    country_name = "Taiwan"
                elif (country_name == "Korea, South"):
                    country_name = "South Korea"
                elif (country_name == "US"):
                    country_name = "United States"
                elif (country_name == "Congo (Brazzaville)"):
                    country_name = "Congo-Brazzaville"
                elif (country_name == "Congo (Kinshasa)"):
                    country_name = "Congo-Kinshasa"

                country_code = get_country_code(country_name, c)
                if country_code is None:
                    missing_countries_set.add(country_name)
                else:
                    region_name = row.Province_State
                    if (region_name is None):   # a country-level entry
                        prev_death = 0 if country_code not in prev_death_dict else prev_death_dict[country_code]
                        prev_recovered = 0 if country_code not in prev_recovered_dict else prev_recovered_dict[country_code]
                        prev_case = 0 if country_code not in prev_case_dict else prev_case_dict[country_code]
                        sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                        # handles the case of a blank column by inserting None
                        c.execute(sql,(country_code, date, src_id, row.Deaths - prev_death if row.Deaths is not None else None, row.Confirmed - prev_case if row.Confirmed is not None else None, row.Recovered - prev_recovered if row.Recovered is not None else None))
                        # update previous
                        if row.Deaths is not None:
                            prev_death_dict[country_code] = row.Deaths
                        if row.Recovered is not None:
                            prev_recovered_dict[country_code] = row.Recovered
                        if row.Confirmed is not None:
                            prev_case_dict[country_code] = row.Confirmed
                    elif region_name != "Recovered":   # a region-level entry
                        # skip Recovered row - irrelevant data - be on the look out for other special cases that haven't been noticed yet
                        region_code = get_region_code(country_code, region_name, c)
                        if region_code is None:
                            sql = '''INSERT INTO Regions (region_name, country_code, longitude, latitude) VALUES (?, ?, ?, ?)'''
                            c.execute(sql,(region_name, country_code, row.Long_ if 'Long_' in df.columns else None, row.Lat if 'Lat' in df.columns else None))
                            conn.commit()
                            region_code = get_region_code(country_code, region_name, c)
                        prev_death = 0 if region_code not in prev_death_dict else prev_death_dict[region_code]
                        prev_recovered = 0 if region_code not in prev_recovered_dict else prev_recovered_dict[region_code]
                        prev_case = 0 if region_code not in prev_case_dict else prev_case_dict[region_code]
                        sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                        # handles the case of a blank column by inserting None
                        c.execute(sql,(region_code, date, src_id, row.Deaths - prev_death if row.Deaths is not None else None, row.Confirmed - prev_case if row.Confirmed is not None else None, row.Recovered - prev_recovered if row.Recovered is not None else None))
                        # update previous
                        if row.Deaths is not None:
                            prev_death_dict[region_code] = row.Deaths
                        if row.Recovered is not None:
                            prev_recovered_dict[region_code] = row.Recovered
                        if row.Confirmed is not None:
                            prev_case_dict[region_code] = row.Confirmed
            conn.commit()   # runs after every csv
        except:
            break
        dt += datetime.timedelta(days=1)
