import pandas as pd
import sqlite3
import sys
import datetime
import requests
from datetime import date

sys.path.append("..")
from util import *

#install html parse tool
from urllib.request import urlopen
!pip install beautifulsoup4
from bs4 import BeautifulSoup
from urllib.request import urlopen

#update country and county level case data and vaccination data for country and state
def update_us():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
    
    
    # get country_code for US
    us_code = get_country_code("United States", c)
    
    #get source id for US data
    us_src_url = "https://github.com/nytimes/covid-19-data"
    us_src = get_source_id(us_src_url, c)
    us_src_v = "https://covid.cdc.gov/covid-data-tracker/#datatracker-home"
    us_src_v = get_source_id(us_src_v, c)
    
    us_country = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us.csv")
    #us_state = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-states.csv")
    us_county = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-recent.csv")
    us_sv = pd.read_csv("https://data.cdc.gov/api/views/rh2h-3yt2/rows.csv")
    
    #insert data for US
    us_country = us_country[::-1]
    for index, row in us_country.iterrows():
        date1 = row['date']
        c.execute('SELECT * FROM Cases_Per_Country WHERE country_code ="' + us_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
            c.execute(sql,(us_code, row["date"], us_src, row["deaths"], row["cases"]))
        else:
            break
    conn.commit()
    
    region_dict = {}
    #get state code for US
    c.execute("SELECT region_code, region_name from Regions Where country_code = 'US'")
    result = c.fetchall()

    for i in range(0,len(result)):
        region_dict[result[i][1]] = result[i][0]
    
    #insert county code and data
    
    us_county = us_county[::-1]
    for index, row in us_county.iterrows():
        state = row["state"]
        county = row["county"]
        county_code = get_district_code(region_dict[state], county, c)
        date1 = row['date']
        c.execute('SELECT * FROM Cases_Per_District WHERE district_code=' + str(county_code) + ' AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            sql = '''INSERT INTO Cases_Per_District (district_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
            c.execute(sql,(county_code, row["date"], us_src, row["deaths"], row["cases"]))
        else:
            break
    conn.commit()
    
    #get abb 
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
    abb["PW"] = "Palau"
    abb["MH"] = "Marshall Islands"
    abb["FM"] = "Federated States of Micronesia"
    
    #insert vaccination data for country and state
    for index, row in us_sv.iterrows():
        date1 = row['Date']
        c.execute('SELECT * FROM Vaccinations_Per_Country WHERE country_code ="' + us_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            if row["date_type"] == "Report":
                if row["Location"] == "US":
                    sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                    c.execute(sql,(row["Date"], row["Admin_Dose_1_Cumulative"], row["Series_Complete_Cumulative"], row["Booster_Cumulative"], us_code, us_src_v))
                else:
                    sql = '''INSERT INTO Vaccinations_Per_Region (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, region_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                    c.execute(sql,(row["Date"], row["Admin_Dose_1_Cumulative"], row["Series_Complete_Cumulative"], row["Booster_Cumulative"], region_dict[abb[row["Location"]]], us_src_v))
        else:
            break
    conn.commit()