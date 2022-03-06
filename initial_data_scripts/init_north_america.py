# JHU data for US states is handled in init_global.py
import pandas as pd
import sqlite3
import sys
import datetime
from datetime import date
import requests

sys.path.append("..")
from util import *

#install html parse tool
from urllib.request import urlopen
!pip install beautifulsoup4
from bs4 import BeautifulSoup
from urllib.request import urlopen

def toint(s):
    if pd.isna(s):
        s = "NULL"
    else:
        s = int(s)
    return s

#add country and county level case data and vaccination data for country and state
def init_us():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
    
    
    # get country_code for US
    us_code = get_country_code("United States", c)
    
    #insert and get source id for US data
    us_src_url = "https://github.com/nytimes/covid-19-data"
    set_source(us_src_url, c, conn)
    us_src = get_source_id(us_src_url, c)
    us_src_v = "https://covid.cdc.gov/covid-data-tracker/#datatracker-home"
    set_source(us_src_v, c, conn)
    us_src_v = get_source_id(us_src_v, c)
    
    us_country = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us.csv")
    us_state = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-states.csv")
    us_county = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-recent.csv")
    us_sv = pd.read_csv("https://data.cdc.gov/api/views/rh2h-3yt2/rows.csv")
    
    #insert data for US
    for index, row in us_country.iterrows():
        sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
        c.execute(sql,(us_code, row["date"], us_src, row["deaths"], row["cases"]))
    conn.commit()
    
    county_dict = {}
    region_dict = {}
    #get state code for US
    c.execute("SELECT region_code, region_name from Regions Where country_code = 'US'")
    result = c.fetchall()

    for i in range(0,len(result)):
        region_dict[result[i][1]] = result[i][0]
        county_dict[result[i][1]] = {}
    #insert county code and data
  
    
    for index, row in us_county.iterrows():
        state = row["state"]
        county = row["county"]
        if state not in region_dict:
            sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
            c.execute(sql,(state, us_code))
            region_dict[state] = get_region_code(us_code, state, c)
            county_dict[state] = {}
        if county not in county_dict[state]:
            sql = '''INSERT INTO Districts (district_name, region_code) VALUES (?, ?)'''
            c.execute(sql,(county, region_dict[state]))
            county_dict[state][county] = get_district_code(region_dict[state], county, c)
        sql = '''INSERT INTO Cases_Per_District (district_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
        c.execute(sql,(county_dict[state][county], row["date"], us_src, row["deaths"], row["cases"]))
    conn.commit()
    print(county_dict)
    
    #get and insert population data
    abb = {}
    wikiurl="https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States#cite_note-:0-18"
    table_class="wikitable sortable jquery-tablesorter"
    response=requests.get(wikiurl)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table',{'class':"wikitable"})
    us_abb = pd.read_html(str(table))
    for i in range(0, 3):
        us_abb1 = pd.DataFrame(us_abb[i])
        for index, row in us_abb1.iterrows():
            state = row[0]
            state = state.replace("[D]", "")
            state = state.replace("U.S. ", "")
            abb[row[1]] = state
            if state not in region_dict:
                sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
                c.execute(sql,(state, us_code))
                region_dict[state] = get_region_code(us_code, state, c)
            sql = '''INSERT INTO Population_Per_Region (region_code, population_amount, date_collected) VALUES (?, ?, ?)'''
            c.execute(sql,(region_dict[state], row[5], datetime.datetime(2020, 4, 1).date()))
    sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
    c.execute(sql,("Palau", us_code))
    region_dict["Palau"] = get_region_code(us_code, "Palau", c)
    sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
    c.execute(sql,("Marshall Islands", us_code))
    region_dict["Marshall Islands"] = get_region_code(us_code, "Marshall Islands", c)
    sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
    c.execute(sql,("Federated States of Micronesia", us_code))
    region_dict["Federated States of Micronesia"] = get_region_code(us_code, "Federated States of Micronesia", c)
    abb["PW"] = "Palau"
    abb["MH"] = "Marshall Islands"
    abb["FM"] = "Federated States of Micronesia"
    conn.commit()
    
    sql = '''INSERT INTO Population_Per_Country (country_code, population_amount, date_collected) VALUES (?, ?, ?)'''
    c.execute(sql,(us_code, 334735155, datetime.datetime(2020, 4, 1).date()))   
    conn.commit()
    
    #insert vaccination data for country and state
    for index, row in us_sv.iterrows():
        if row["date_type"] == "Report":
            if row["Location"] == "US":
                sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(row["Date"], row["Admin_Dose_1_Cumulative"], row["Series_Complete_Cumulative"], row["Booster_Cumulative"], us_code, us_src_v))
            else:
                sql = '''INSERT INTO Vaccinations_Per_Region (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, region_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(row["Date"], row["Admin_Dose_1_Cumulative"], row["Series_Complete_Cumulative"], row["Booster_Cumulative"], region_dict[abb[row["Location"]]], us_src_v))
    conn.commit()

def init_canada():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
    
    # get country_code for Canada
    ca_code = get_country_code("Canada", c)
    
    #insert and get source id for Canada data
    ca_src_url = "https://health-infobase.canada.ca/covid-19/epidemiological-summary-covid-19-cases.html?redir=1#a8"
    set_source(ca_src_url, c, conn)
    ca_src = get_source_id(ca_src_url, c)
    
    ca_case = pd.read_csv("https://health-infobase.canada.ca/src/data/covidLive/covid19-download.csv")
    ca_v = pd.read_csv("https://health-infobase.canada.ca/src/data/covidLive/vaccination-coverage-map.csv")
    ca_s = pd.read_csv("https://health-infobase.canada.ca/src/data/covidLive/covid19-epiSummary-variants.csv")
    
    #insert country and region case data
    region_dict = {}
    for index, row in ca_case.iterrows():
        region = row["prname"]
        case = row["numconf"]
        death = toint(row["numdeaths"])
        recover = toint(row["numrecover"])
        if region == "Canada":
            sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(ca_code, row["date"], ca_src, death, case, recover))
        else:
            if region not in region_dict:
                sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
                c.execute(sql,(region, ca_code))
                region_dict[region] = get_region_code(ca_code, region, c)
            sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(region_dict[region], row["date"], ca_src, death, case, recover))
    conn.commit()
    
    #insert country and region vaccination data
    for index, row in ca_v.iterrows():
        region = row["prename"]
        first = row["numtotal_atleast1dose"]
        second = toint(row["numtotal_fully"])
        third = toint(row["numtotal_additional"])
        if region == "Canada":
            sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(row["week_end"], first, second, third, ca_code, ca_src))
        else:
            sql = '''INSERT INTO Vaccinations_Per_Region (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, region_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(row["week_end"], first, second, third, region_dict[region], ca_src))
    conn.commit()
    
    #insert strain data for canada country 
    ca_strain = {}
    for index, row in ca_s.iterrows():
        if row["Variant Grouping"] == "VOC":
            if row["Collection (week)"] not in ca_strain:
                ca_strain[row["Collection (week)"]] = {"Alpha":0 , "Beta": 0, "Gamma" :0, "Delta": 0, "Omicron": 0}
            ca_strain[row["Collection (week)"]][row["_Identifier"]] = ca_strain[row["Collection (week)"]][row["_Identifier"]] + row["%CT Count of Sample #"]   
    for date in ca_strain:
        sql = '''INSERT INTO Strains_Per_Country (date_collected, country_code, source_id, alpha_rate, beta_rate, gamma_rate, delta_rate, omicron_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        c.execute(sql,(date, ca_code, ca_src, ca_strain[date]["Alpha"], ca_strain[date]["Beta"], ca_strain[date]["Gamma"],ca_strain[date]["Delta"], ca_strain[date]["Omicron"]))
    conn.commit()
    
    #insert population data for country and region
    sql = '''INSERT INTO Population_Per_Country (country_code, population_amount, date_collected) VALUES (?, ?, ?)'''
    c.execute(sql,(ca_code, 38436447, datetime.datetime(2022, 2, 27).date()))
    conn.commit()
    
    wikiurl="https://en.wikipedia.org/wiki/Provinces_and_territories_of_Canada"
    table_class="wikitable sortable jquery-tablesorter"
    response=requests.get(wikiurl)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table',{'class':"wikitable"})
    ca_p = pd.read_html(str(table))
    for i in range(0, 2):
        ca_p1 = pd.DataFrame(ca_p[i])
        for index, row in ca_p1.iterrows():
            state = row[0]
            state = state.replace("[b]", "")
            if "Total" not in state:
                sql = '''INSERT INTO Population_Per_Region (region_code, population_amount, date_collected) VALUES (?, ?, ?)'''
                c.execute(sql,(region_dict[state], row[6], datetime.datetime(2021, 8, 20).date()))
    conn.commit()

def init_guatemala():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
    
    # get country_code for Guatemala
    gu_code = get_country_code("Guatemala", c)
    
    #insert and get source id for US data
    gu_src_url = "https://tablerocovid.mspas.gob.gt/"
    set_source(gu_src_url, c, conn)
    gu_src = get_source_id(gu_src_url, c)
    
    v_src = "https://github.com/owid/covid-19-data"
    set_source(v_src, c, conn)
    v_src = get_source_id(v_src, c)
    
    gu_death = pd.read_csv("https://gtmvigilanciacovid.shinyapps.io/1GEAxasgYEyITt3Y2GrQqQFEDKW89fl9/_w_0d14592e/session/1f0e3b3486ac8317dfaad7a0be3f8481/download/fallecidosFF?w=0d14592e")
    gu_case = pd.read_csv("https://gtmvigilanciacovid.shinyapps.io/1GEAxasgYEyITt3Y2GrQqQFEDKW89fl9/_w_0d14592e/session/1f0e3b3486ac8317dfaad7a0be3f8481/download/confirmadosFER?w=0d14592e")
    gu_v = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/Guatemala.csv")
    gu = pd.merge(gu_case, gu_death, on=["departamento", "municipio"])
    

    #insert district case data and population data for guatemala
    region_dict = {}
    city_dict = {}
    for index, row in gu.iterrows():
        if index >= 1:
            region = row["departamento"]
            city = row["municipio"]
            if region not in region_dict:
                sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
                c.execute(sql,(region, gu_code))
                region_dict[region] = get_region_code(gu_code, region, c)
                city_dict[region] = {}
            if city not in city_dict[region]:
                sql = '''INSERT INTO Districts (district_name, region_code) VALUES (?, ?)'''
                c.execute(sql,(city, region_dict[region]))
                city_dict[region][city] = get_district_code(region_dict[region], city, c)
            for i in range(5, len(row) - 1):
                if "_x" in gu.columns[i]:
                    date1 = gu.columns[i].replace("_x", "")
                    case = check(row[i])
                    death = check(row[date1 + "_y"])
                    sql = '''INSERT INTO Cases_Per_District (district_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
                    c.execute(sql,(city_dict[region][city], date1, gu_src, death, case))
            sql = '''INSERT INTO Population_Per_District (district_code, population_amount, date_collected) VALUES (?, ?, ?)'''
            c.execute(sql,(city_dict[region][city], check(row["poblacion_x"]), date.today()))
    conn.commit()
    
    #insert vaccination country data for guatemala
    for index, row in gu_v.iterrows():
        sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
        c.execute(sql, (row["date"], toint(row["people_vaccinated"]), toint(row["people_fully_vaccinated"]), toint(row["total_boosters"]), gu_code, v_src))
    conn.commit()