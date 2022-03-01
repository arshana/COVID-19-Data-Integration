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
    # get country_code
    us_code = get_country_code("United States", c)    
    
    # intentionally selected this csv compared to some of the others to ensure all rows are covered
    setup_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/02-27-2022.csv")

    # change Burma to Myanmar
    # change Czechia to Czech Republic
    # if country not in Countries, skip
    # change Taiwan* to Taiwan
    # change Korea, South to "Korea, Republic of"
    # what's up with Namibia?

