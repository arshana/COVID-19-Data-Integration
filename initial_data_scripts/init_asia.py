import pandas as pd
import sqlite3
import sys

sys.path.append("..")

from util import *

#install translator
!pip install google_trans_new
from google_trans_new import google_translator  
translator = google_translator() 

def init_japan():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
    
    # get country_code for Japan
    japan_code = get_country_code("Japan", c)
    
    #insert and get source id for Japan data
    japan_src1_url = "https://covid19.mhlw.go.jp/en/"
    set_source(japan_src1_url, c, conn)
    japan_src2_url = "https://www.kantei.go.jp/jp/headline/kansensho/vaccine.html"
    set_source(japan_src2_url, c, conn)
    japan_src1 = get_source_id(japan_src1_url, c)
    japan_src2 = get_source_id(japan_src2_url, c)
    
    #get newly confirmed data and death data for Japan
    japan = pd.read_csv("https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv")
    japan_death = pd.read_csv("https://covid19.mhlw.go.jp/public/opendata/number_of_deaths_daily.csv")
    japan_all = pd.merge(japan, japan_death, on=["Date"])
    
    #insert regions tables 
    for col in japan.columns:
        sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
        if col != "Date" and col != "ALL":
            c.execute(sql,(col, japan_code))
    conn.commit()
    
    #insert daily data for Japan
    for row in japan_all.itertuples(index=True, name='Pandas'):
        sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
        c.execute(sql,(japan_code, row.Date, japan_src1, row.ALL_y, row.ALL_x))
    conn.commit()
    
    #get region_code for Japan city
    c.execute("SELECT region_code, region_name from Regions")
    result = c.fetchall()
    japan_region = []
    region_dict = {}
    for i in range(0,len(result)):
        japan_region.append([result[i][0], result[i][1] + "_x", result[i][1] + "_y"])
        region_dict[result[i][1]] = result[i][0]

    #insert region daily case data
    for index, row in japan_all.iterrows():
        sql = '''INSERT INTO Cases_Per_Region(region_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
        for city in japan_region:
            c.execute(sql,(city[0], row['Date'], japan_src1, row[city[2]], row[city[1]]))
    conn.commit()
    
    #get Japan vaccianation data(include population data)
    japan_vs = pd.ExcelFile("https://www.kantei.go.jp/jp/content/kenbetsu-vaccination_data2.xlsx")
    sheets = japan_vs.sheet_names
    japan_v = pd.read_excel(japan_vs, sheets[2])
    
    #insert vaccianation data and population data for Japan  
    from datetime import date
    for index, row in japan_v.iterrows():
        if index == 5:
            rate = row[3]
            sql = '''INSERT INTO Vaccinations_Per_Country (vaccination_rate, country_code, source_id) VALUES (?, ?, ?)'''
            c.execute(sql,(rate, japan_code, japan_src2))
            sql = '''INSERT INTO Population_Per_Country (country_code, population_amount, date_collected) VALUES (?, ?, ?)'''
            c.execute(sql,(japan_code, row[12], date.today()))
            break
    conn.commit()
    
    #insert vaccianation data and population data for cities of Japan 
    for index, row in japan_v.iterrows():
        if index >=6 and index <= 52:
            city = translator.translate(row[0])
            city = city.split()[1]
            rate = row[3]
            sql = '''INSERT INTO Vaccinations_Per_Region (vaccination_rate, region_code, source_id) VALUES (?, ?, ?)'''
            c.execute(sql,(rate, region_dict[city], japan_src2))
            sql = '''INSERT INTO Population_Per_Region (region_code, population_amount, date_collected) VALUES (?, ?, ?)'''
            c.execute(sql,(region_dict[city], row[12], date.today()))
    conn.commit()
    conn.close()

def init_korea():

    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()

    # get country_code for Korea
    korea_code = get_country_code("Korea, Republic of", c)

    #insert and get source id for Japan data
    korea_src_url = "http://ncov.mohw.go.kr/index.jsp"
    set_source(korea_src_url, c, conn)
    korea_src = get_source_id(korea_src_url, c)

    #get korea data
    korea = pd.ExcelFile("http://ncov.mohw.go.kr/upload/ncov/file/202202/1645425583350_20220221153943.xlsx")
    sheets = korea.sheet_names
    korea_case = pd.read_excel(korea, sheets[3])
    korea_death = pd.read_excel(korea, sheets[0])
    korea_death = korea_death.replace("-", 0)
    korea_case = korea_case.replace("-", 0)
    korea = pd.merge(korea_case, korea_death, on=["Unnamed: 0"])

    #insert region table
    index_region = {}
    region_dict = {}
    for index, row in korea_case.iterrows():
        if index == 3:
            for i in range(2, len(row) - 1):
                city = translator.translate(row[i])
                if city == "game ":
                    city = "Gyeonggi"
                sql = '''INSERT INTO Regions (region_name, country_code) VALUES (?, ?)'''
                c.execute(sql,(city, korea_code))
                city_code = get_region_code(korea_code, city, c)
                index_region[i] = (city, city_code)
                region_dict[city] = city_code
    conn.commit()

    #insert data for korea and region of it
    for index, row in korea.iterrows():
        if index >= 11:
            date = row[0]
            cases = row[1]
            death =  row["Unnamed: 4_y"]
            sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
            c.execute(sql,(korea_code, date, korea_src, death, cases))
            sql = '''INSERT INTO Cases_Per_Region(region_code, date_collected, source_id, case_numbers) VALUES (?, ?, ?, ?)'''
            for i in range(2, 18):
                city = index_region[i][0]
                city_code = index_region[i][1]
                c.execute(sql,(city_code, date, korea_src, row[i]))
    conn.commit()
    conn.close()
    