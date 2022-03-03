import pandas as pd
import sqlite3
import sys
import datetime
from datetime import date

sys.path.append("..")
from util import *

#install translator
!pip install google_trans_new
from google_trans_new import google_translator  
translator = google_translator() 

#install html parse tool
from urllib.request import urlopen
!pip install beautifulsoup4
from bs4 import BeautifulSoup
from urllib.request import urlopen

def string_to_int(s):
    return s.replace(",", "").strip()


def update_korea():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
	korea_code = get_country_code("Korea, Republic of", c)
    korea_src_url = "http://ncov.mohw.go.kr/index.jsp"
    korea_src = get_source_id(korea_src_url, c)
    url = "http://ncov.mohw.go.kr/"
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all('a'):
        s_index = str(link).find("file_path=")
        if s_index != -1:
            e_index = str(link).find("><span>")
            k_url = "http://ncov.mohw.go.kr" + str(link)[s_index + 10 :e_index - 1]
            break
    korea = pd.ExcelFile(k_url)
    sheets = korea.sheet_names
    korea_case = pd.read_excel(korea, sheets[3])
    korea_age = pd.read_excel(korea, sheets[1])
    korea_death = pd.read_excel(korea, sheets[0])
    korea_death = korea_death.replace("-", 0)
    korea_case = korea_case.replace("-", 0)
    korea_age = korea_age.replace("-", 0)
    korea = pd.merge(korea_case, korea_death, on=["Unnamed: 0"])
    
    #insert region table
    index_region = {}
    region_dict = {}
    for index, row in korea_case.iterrows():
        if index == 3:
            for i in range(2, len(row) - 1):
                city = translator.translate(row[i]).replace(" ", "")
                if city == "game":
                    city = "Gyeonggi"
                city_code = get_region_code(korea_code, city, c)
                index_region[i] = (city, city_code)
                region_dict[city] = city_code

    #insert data for korea and region of it
    for index, row in korea.iterrows():
        if index >= 11:
            date1 = row[0].date()
            c.execute('SELECT * FROM Cases_Per_Country WHERE country_code ="' + korea_code + '" AND date_collected ="' + str(date1)+ '"')
            result = c.fetchall()
            if len(result) == 0:
                cases = row[1]
                death =  row["Unnamed: 4_y"]
                sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
                c.execute(sql,(korea_code, date1, korea_src, death, cases))
                sql = '''INSERT INTO Cases_Per_Region(region_code, date_collected, source_id, case_numbers) VALUES (?, ?, ?, ?)'''
                for i in range(2, 18):
                    city = index_region[i][0]
                    city_code = index_region[i][1]
                    c.execute(sql,(city_code, date1, korea_src, row[i]))
    conn.commit()
    
    #insert data for korea age
    age_group = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "over 80"]
    for index, row in korea_age.iterrows():
        if index >= 5:
            date1 = row[0].date()
            c.execute('SELECT * FROM Age_Per_Country WHERE country_id ="' + korea_code + '" AND date_collected ="' + str(date1)+ '"')
            result = c.fetchall()
            if len(result) == 0:
                for i in range(0, 9):
                    case = row[i + 2]
                    sql = '''INSERT INTO Age_Per_Country (date_collected, country_id, source_id, age_group, case_number) VALUES (?, ?, ?, ?, ?)'''
                    c.execute(sql,(date1, korea_code, korea_src,age_group[i], case))
    conn.commit()
    
    #get vaccination number data for korea
    date1 = date.today()
    c.execute('SELECT * FROM Vaccinations_Per_Country WHERE country_code ="' + korea_code + '" AND date_collected ="' + str(date1)+ '"')
    result = c.fetchall()
    if len(result) == 0:
        url = "https://ncv.kdca.go.kr/mainStatus.es?mid=a11702000000"
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()
        text1 = translator.translate(text)
        text1 = text1.splitlines()
        v = {}
        for i in range(0, len(text1)):
            line = text1[i]
            if line == "Cumulative A + B":
                v1 = int(string_to_int(text1[i + 1]))
                v2 = int(string_to_int(text1[i + 2]))
                v3 = int(string_to_int(text1[i + 3]))
                v["all"] = [v1, v2, v3]
            if line == "game":
                v1 = int(string_to_int(text1[i + 2]))
                v2 = int(string_to_int(text1[i + 4]))
                v3 = int(string_to_int(text1[i + 6]))
                v["Gyeonggi"] = [v1, v2, v3]
            if line in region_dict.keys():
                v1 = int(string_to_int(text1[i + 2]))
                v2 = int(string_to_int(text1[i + 4]))
                v3 = int(string_to_int(text1[i + 6]))
                v[line] = [v1, v2, v3]

        #Insert vaccinations data for korea
        sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
        c.execute(sql,(date.today(), v["all"][0], v["all"][1], v["all"][2], korea_code, korea_src))
        conn.commit()

        for city in region_dict.keys():
            city_code = region_dict[city]
            sql = '''INSERT INTO Vaccinations_Per_Region (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, region_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(date.today(), v[city][0], v[city][1], v[city][2], city_code, korea_src))
        conn.commit()
    conn.close()

def update_japan():
    conn = sqlite3.connect('prototype_db')
    c = conn.cursor()
    
    # get country_code for Japan
    japan_code = get_country_code("Japan", c)
    
    #get source id for Japan data
    japan_src1_url = "https://covid19.mhlw.go.jp/en/"
    japan_src2_url = "https://www.kantei.go.jp/jp/headline/kansensho/vaccine.html"
    japan_src1 = get_source_id(japan_src1_url, c)
    japan_src2 = get_source_id(japan_src2_url, c)
    
    #get newly confirmed data and death data for Japan
    japan = pd.read_csv("https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv")
    japan_death = pd.read_csv("https://covid19.mhlw.go.jp/public/opendata/number_of_deaths_daily.csv")
    japan_age = pd.read_csv("https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_detail_weekly.csv")
    japan_all = pd.merge(japan, japan_death, on=["Date"])
    
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
        date1 = row['Date']
        c.execute('SELECT * FROM Cases_Per_Country WHERE country_code ="' + japan_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
            c.execute(sql,(japan_code, row['Date'], japan_src1, row["ALL_y"], row["ALL_x"]))
            sql = '''INSERT INTO Cases_Per_Region(region_code, date_collected, source_id, death_numbers, case_numbers) VALUES (?, ?, ?, ?, ?)'''
            for city in japan_region:
                c.execute(sql,(city[0], row['Date'], japan_src1, row[city[2]], row[city[1]]))
    conn.commit()
    
    #insert country,region age data
    null = "NULL"
    cities = japan_age.columns
    for index,row in japan_age.iterrows():
        age_group = row
        break
    for index,row in japan_age.iterrows():
        d = row[0].find("~")
        date1 = row[0][d + 1:]
        if index >= 1:
            c.execute('SELECT * FROM Age_Per_Country WHERE country_id ="' + japan_code + '" AND date_collected ="' + str(date1)+ '"')
            result = c.fetchall()
            if len(result) == 0:
                for i in range(0, len(cities)):
                    if cities[i].find("Unnamed") == -1:
                        if cities[i] == "ALL":
                            for j in range(0, 20):
                                age = age_group[i + j]
                                case = row[i + j]
                                sql = '''INSERT INTO Age_Per_Country (date_collected, country_id, source_id, age_group, case_number) VALUES (?, ?, ?, ?, ?)'''
                                c.execute(sql,(date1, japan_code, japan_src1, age, case))
                        else:
                            for j in range(0, 20):
                                age = age_group[i + j]
                                case = row[i + j]
                                if pd.isna(case) or case == "*":
                                    case = null
                                sql = '''INSERT INTO Age_Per_Region (date_collected, region_id, source_id, age_group, case_number) VALUES (?, ?, ?, ?, ?)'''
                                c.execute(sql,(date1, region_dict[cities[i]], japan_src1, age, case))
    conn.commit()
    
    #update vaccianation data
    date1 = date.today()
    c.execute('SELECT * FROM Vaccinations_Per_Country WHERE country_code ="' + japan_code + '" AND date_collected ="' + str(date1)+ '"')
    result = c.fetchall()
    if len(result) == 0:
        japan_vs = pd.ExcelFile("https://www.kantei.go.jp/jp/content/kenbetsu-vaccination_data2.xlsx")
        sheets = japan_vs.sheet_names
        japan_v = pd.read_excel(japan_vs, sheets[2]) 
    
        for index, row in japan_v.iterrows():
            if index == 5:
                rate1 = row[2]
                rate2 = row[4]
                rate3 = row[6]
                sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(date.today(), rate1, rate2, rate3, japan_code, japan_src2))
                break
        conn.commit()
    
        #insert vaccianation data and population data for cities of Japan 
        for index, row in japan_v.iterrows():
            if index >=6 and index <= 52:
                city = translator.translate(row[0])
                city = city.split()[1]
                rate1 = row[2]
                rate2 = row[4]
                rate3 = row[6]
                sql = '''INSERT INTO Vaccinations_Per_Region (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, region_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
                c.execute(sql,(date.today(), rate1, rate2, rate3, region_dict[city], japan_src2))
    conn.commit()
    c.close()