import pandas as pd
import sqlite3
import sys
import datetime
from datetime import date
import requests
sys.path.append("..")
from util import *

def inti_global_v():
    conn = sqlite3.connect('sqlite_db')
    c = conn.cursor()

    v_src_url = "https://github.com/owid/covid-19-data"
    set_source(v_src_url, c, conn)
    v_src = get_source_id(v_src_url, c)

    c.execute("select * from Countries")
    result = c.fetchall()
    for country in result:
        link = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/" + country[1]+ ".csv" 
        data = "Null"
        try:
            data = pd.read_csv(link)
        except:
            continue
        c_code = get_country_code(country[1], c)
        if country[1] == "Palau":
            continue
        for index, row in data.iterrows():
            sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql, (row["date"], toint(row["people_vaccinated"]), toint(row["people_fully_vaccinated"]), toint(row["total_boosters"]), c_code, v_src))
    conn.commit()