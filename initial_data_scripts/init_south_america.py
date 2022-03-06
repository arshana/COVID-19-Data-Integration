import pandas as pd
import sqlite3
import sys
import datetime
from datetime import date
import requests

sys.path.append("..")

from util import *

def toint(s):
    if pd.isna(s):
        s = "NULL"
    else:
        s = int(s)
    return s

def init_brazil():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
    
    # get country_code for brazil
    br_code = get_country_code("Brazil", c)
    
    #insert and get source id for brazil data
    br_src_url = "https://github.com/wcota/covid19br"
    set_source(br_src_url, c, conn)
    br_src = get_source_id(br_src_url, c)
    
    br = pd.read_csv("https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv")
    br_city = pd.read_csv("https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-cities.csv")
    
    #insert country, state case  vaccination data 
    region_dict = {}
    city_dict = {}
    for index, row in br.iterrows():
        region = row["state"]
        case = row["newDeaths"]
        death = row["newDeaths"]
        recover = row["recovered"]
        first = toint(row["vaccinated"])
        second = toint(row["vaccinated_second"])
        third = toint(row["vaccinated_third"])
        if region == "TOTAL":
            sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(br_code, row["date"], br_src, death, case, recover))
            if (first != "NULL"):
                sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(row["date"], first, second, third, br_code, br_src))
        else:
            if region not in region_dict:
                sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
                c.execute(sql,(region, br_code))
                region_dict[region] = get_region_code(br_code, region, c)
                city_dict[region] = {} 
            sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(region_dict[region], row["date"], br_src, death, case, recover))
            if (first != "NULL"):
                sql = '''INSERT INTO Vaccinations_Per_Region (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, region_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(row["date"], first, second, third, region_dict[region], br_src))
    conn.commit()
    
    #insert population for brazil
    sql = '''INSERT INTO Population_Per_Country (country_code, population_amount, date_collected) VALUES (?, ?, ?)'''
    c.execute(sql,(br_code, 210147125, datetime.datetime(2018, 8, 30).date()))
    conn.commit()
    
    #insert city case data for brazil
    for index, row in br_city.iterrows():
        region = row["state"]
        city = row["city"]
        if city not in city_dict[region]:
            sql = '''INSERT INTO Districts (district_name, region_code) VALUES (?, ?)'''
            c.execute(sql,(city, region_dict[region]))
            city_dict[region][city] = get_district_code(region_dict[region], city, c)
        sql = '''INSERT INTO Cases_Per_District (district_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
        c.execute(sql,(city_dict[region][city], row["date"], br_src, row["newDeaths"], row["newCases"]))
    conn.commit()