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

def update_brazil():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
    
    # get country_code for brazil
    br_code = get_country_code("Brazil", c)
    
    #insert and get source id for brazil data
    br_src_url = "https://github.com/wcota/covid19br"
    br_src = get_source_id(br_src_url, c)
    
    br = pd.read_csv("https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv")
    br_city = pd.read_csv("https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-cities.csv")
    
    #insert country, state case  vaccination data 
    for index, row in br.iterrows():
        region = row["state"]
        case = row["newDeaths"]
        death = row["newDeaths"]
        recover = row["recovered"]
        first = toint(row["vaccinated"])
        second = toint(row["vaccinated_second"])
        third = toint(row["vaccinated_third"])
        if region == "TOTAL":
            c.execute('SELECT * FROM Cases_Per_Country WHERE country_code ="' + br_code + '" AND date_collected ="' + str(date1)+ '"')
            result = c.fetchall()
            if len(result) == 0:
                sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(br_code, row["date"], br_src, death, case, recover))
                if (first != "NULL"):
                    sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                    c.execute(sql,(row["date"], first, second, third, br_code, br_src))
            else:
                break
        else:
            region_code = get_region_code(br_code, region, c)
            c.execute('SELECT * FROM Cases_Per_Region WHERE region_code ="' + region_code + '" AND date_collected ="' + str(date1)+ '"')
            result = c.fetchall()
            if len(result) == 0: 
                sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(region_dict[region], row["date"], br_src, death, case, recover))
                if (first != "NULL"):
                    sql = '''INSERT INTO Vaccinations_Per_Region (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, region_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                    c.execute(sql,(row["date"], first, second, third, region_dict[region], br_src))
            else:
                break
    conn.commit()
    
    #insert new city case data for brazil
    for index, row in br_city.iterrows():
        region = row["state"]
        city = row["city"]
        region_code = get_region_code(br_code, region, c)
        city_dict[region][city] = get_district_code(region_code, city, c)
        sql = '''INSERT INTO Cases_Per_District (district_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
        c.execute(sql,(city_code, row["date"], br_src, row["newDeaths"], row["newCases"]))
    conn.commit()