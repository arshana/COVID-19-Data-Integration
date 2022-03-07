import pandas as pd
import sqlite3
import sys
import datetime
from datetime import date
import requests

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

def toint1(s):
    if pd.isna(s):
        s = 0
    else:
        s = int(s)
    return s

def update_korea():
    conn = sqlite3.connect('sqlite_db')
    c = conn.cursor()
    
    korea_code = get_country_code("South Korea", c)
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
    
    korea = korea[::-1]
    #insert data for korea and region of it
    for index, row in korea.iterrows():
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
        else:
            break
    conn.commit()
    
    #insert data for korea age
    korea_age = korea_age[::-1]
    age_group = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "over 80"]
    for index, row in korea_age.iterrows():
        date1 = row[0].date()
        c.execute('SELECT * FROM Age_Per_Country WHERE country_code ="' + korea_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            for i in range(0, 9):
                case = row[i + 2]
                sql = '''INSERT INTO Age_Per_Country (date_collected, country_code, source_id, age_group, case_number) VALUES (?, ?, ?, ?, ?)'''
                c.execute(sql,(date1, korea_code, korea_src,age_group[i], case))
        else:
            break
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
    conn = sqlite3.connect('sqlite_db')
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
    c.execute("SELECT region_code, region_name from Regions Where country_code = 'JP'")
    result = c.fetchall()
    japan_region = []
    region_dict = {}
    for i in range(0,len(result)):
        japan_region.append([result[i][0], result[i][1] + "_x", result[i][1] + "_y"])
        region_dict[result[i][1]] = result[i][0]
    
    
    #insert region daily case data
    japan_all = japan_all[::-1]
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
        else:
            break
    conn.commit()
    
    #insert country,region age data
    null = "NULL"
    cities = japan_age.columns
    for index,row in japan_age.iterrows():
        age_group = row
        break
    japan_age = japan_age[::-1]
    for index,row in japan_age.iterrows():
        d = row[0].find("~")
        date1 = datetime.datetime.strptime(row[0][d + 1:], "%Y/%m/%d").date()
        c.execute('SELECT * FROM Age_Per_Country WHERE country_code ="' + japan_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            date1 = datetime.datetime.strptime(row[0][:d], "%Y/%m/%d").date()
            date2 = datetime.datetime.strptime(row[0][d + 1:], "%Y/%m/%d").date()
            while date1 != date2 + datetime.timedelta(days=1):
                for i in range(0, len(cities)):
                    if cities[i].find("Unnamed") == -1:
                        if cities[i] == "ALL":
                            for j in range(0, 20):
                                age = age_group[i + j]
                                case = row[i + j]
                                if pd.isna(case) or case == "*":
                                    case = null
                                else:
                                    case = round(int(row[i + j]) / 7)
                                sql = '''INSERT INTO Age_Per_Country (date_collected, country_code, source_id, age_group, case_number) VALUES (?, ?, ?, ?, ?)'''
                                c.execute(sql,(date1, japan_code, japan_src1, age, case))
                        else:
                            for j in range(0, 20):
                                age = age_group[i + j]
                                case = row[i + j]
                                if pd.isna(case) or case == "*":
                                    case = null
                                else:
                                    case = round(int(row[i + j]) / 7)
                                sql = '''INSERT INTO Age_Per_Region (date_collected, region_code, source_id, age_group, case_number) VALUES (?, ?, ?, ?, ?)'''
                                c.execute(sql,(date1, region_dict[cities[i]], japan_src1, age, case))
                date1 =  date1 + datetime.timedelta(days=1)
        else:
            break
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

def ina():
    conn = sqlite3.connect('sqlite_db')
    c = conn.cursor()
    
    # get country_code for Indonesia
    ina_code = get_country_code("Indonesia", c)
    
    #insert and get source id for Indonesia data
    ina_src_url = "https://github.com/erlange/INACOVID"
    ina_src = get_source_id(ina_src_url, c)
    
    #get data
    ina_case = pd.read_csv("https://raw.githubusercontent.com/erlange/INACOVID/master/data/csv/ext.natl.csv")
    ina_city = pd.read_csv("https://raw.githubusercontent.com/erlange/INACOVID/master/data/csv/ext.prov.csv")
    ina_age_nation = pd.read_csv("https://raw.githubusercontent.com/erlange/INACOVID/master/data/csv/cat.natl.csv")
    ina_age_city = pd.read_csv("https://raw.githubusercontent.com/erlange/INACOVID/master/data/csv/cat.prov.csv")
    ina_v = pd.read_csv("https://raw.githubusercontent.com/erlange/INACOVID/master/data/csv/vax.csv")
    
    #insert data for Indonesia cases
    ina_case = ina_case[::-1]
    for index, row in ina_case.iterrows():
        date1 = row['Date']
        c.execute('SELECT * FROM Cases_Per_Country WHERE country_code ="' + ina_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers, hospitalization_numbers) VALUES (?, ?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(ina_code, row["Date"], ina_src, row["jumlah_meninggal"], row["jumlah_positif"], row["jumlah_sembuh"], row["jumlah_dirawat"]))
        else:
            break
    conn.commit()
    
    #get region_code for Indonesia
    region_dict = {}
    for index, row in ina_city.iterrows():
        if row["Location"] not in region_dict:
            region_dict[row["Location"]] = get_region_code(ina_code, row["Location"], c)
    conn.commit()
    
    ina_city = ina_city[::-1]
    #insert region data for Indonesia
    for index, row in ina_city.iterrows():
        date1 = row['Date']
        c.execute('SELECT * FROM Cases_Per_Region WHERE region_code =' + str(region_dict[row["Location"]]) + ' AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers, hospitalization_numbers) VALUES (?, ?, ?, ?, ?, ?, ?)'''
            c.execute(sql,(region_dict[row["Location"]], row["Date"], ina_src, row["MENINGGAL"], row["KASUS"], row["SEMBUH"], row["DIRAWAT_OR_ISOLASI"]))
        else:
            break
    conn.commit()
    
    #insert country,region age data
    date1 = ina_age_nation["Date"][0]
    c.execute('SELECT * FROM Age_Per_Country WHERE country_code ="' + ina_code + '" AND date_collected ="' + str(date1)+ '"')
    result = c.fetchall()
    if len(result) == 0:
        c.execute('SELECT * FROM Cases_Per_Country WHERE country_code ="' + ina_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        for index, row in ina_age_nation.iterrows():
            if row["Category"] == "kelompok_umur":
                case = round(row["kasus"] * result[0][4] / 100)
                recovery = round(row["sembuh"] * result[0][5] / 100)
                hos = round(row["perawatan"] * result[0][6] / 100)
                death = round(row["meninggal"] * result[0][3] / 100)
                sql = '''INSERT INTO Age_Per_Country (date_collected, country_code, source_id, age_group, case_number, recovery_number, hospitalization_number, death_number) VALUES (?, ?, ?, ?, ?, ?, ? ,?)'''
                c.execute(sql,(row["Date"], ina_code,  ina_src, row["SubCategory"], case, recovery, hos, death))
        conn.commit()  
    
    date1 = ina_age_city["Date"][0]
    c.execute('SELECT * FROM Age_Per_Region WHERE source_id =' + str(ina_src) + ' AND date_collected ="' + str(date1)+ '"')
    result = c.fetchall()
    if len(result) == 0:
        region_data = {}
        for city in region_dict:
            c.execute('SELECT * FROM Cases_Per_Region WHERE region_code =' + str(region_dict[city]) + ' AND date_collected ="' + str(date1)+ '"')
            result = c.fetchall()
            region_data[city] = (result[0][3], result[0][4], result[0][5], result[0][6])
        
        for index, row in ina_age_city.iterrows():
            if row["Category"] == "kelompok_umur":
                result = region_data[row["Location"]]
                case = round(row["kasus"] * result[1] / 100)
                recovery = round(row["sembuh"] * result[2] / 100)
                hos = round(row["perawatan"] * result[3] / 100)
                death = round(row["meninggal"] * result[0] / 100)
                sql = '''INSERT INTO Age_Per_Region (date_collected, region_code, source_id, age_group, case_number, recovery_number, hospitalization_number, death_number) VALUES (?, ?, ?, ?, ?, ?, ? ,?)'''
                c.execute(sql,(row["Date"], region_dict[row["Location"]],  ina_src, row["SubCategory"], case, recovery, hos, death))
        conn.commit()
    
    #inser vaccianation data for the country
    ina_v = ina_v[::-1]
    for index, row in ina_v.iterrows():
        date1 = row['Date']
        c.execute('SELECT * FROM Vaccinations_Per_Country WHERE country_code ="' + ina_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?)'''
            c.execute(sql,(row["Date"], row["jumlah_jumlah_vaksinasi_1_kum"], row["jumlah_jumlah_vaksinasi_2_kum"], ina_code, ina_src))
        else:
            break
    conn.commit() 

def update_india():
    conn = sqlite3.connect('sqlite_db')
    c = conn.cursor()
    
    # get country_code for India
    ind_code = get_country_code("India", c)
    
    #get source id for India data
    ind_src_url = "https://prsindia.org/covid-19/cases"
    ind_src = get_source_id(ind_src_url, c)
    
    v_src = "https://github.com/owid/covid-19-data"
    v_src = get_source_id(v_src, c)
    
    ind_case = pd.read_csv("https://prsindia.org/covid-19/cases/download")
    ind_v = pd.read_csv("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/India.csv")

    #inser country, region case data for india
    lastRegion = ""
    for index,row in ind_case.iterrows():
        region = row["Region"]
        if region != lastRegion:
            i = index + 3
            lastC = 0
            lastR = 0
            lastD = 0
        lastRegion = region
        if index >= i:
            case = toint1(row["Confirmed Cases"]) - lastC
            death = toint1(row["Death"]) - lastD
            recover = toint1(row["Cured/Discharged"]) - lastR
            lastC = toint1(row["Confirmed Cases"])
            lastR = toint1(row["Cured/Discharged"])
            lastD = toint1(row["Death"])
            if region != "World":
                if region == "India":
                    date1 = row["Date"]
                    c.execute('SELECT * FROM Cases_Per_Country WHERE country_code ="' + ind_code + '" AND date_collected ="' + str(date1)+ '"')
                    result = c.fetchall()
                    if len(result) == 0:
                        sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                        c.execute(sql,(ind_code, row["Date"], ind_src, death, case, recover))
                else:
                    date1 = row["Date"]
                    region_code = get_region_code(ind_code, region, c)
                    c.execute('SELECT * FROM Cases_Per_Region WHERE region_code ="' + region_code + '" AND date_collected ="' + str(date1)+ '"')
                    result = c.fetchall()
                    if len(result) == 0:
                        sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                        c.execute(sql,(region_dict[region], row["Date"], ind_src, death, case, recover))
    conn.commit()
    
    #insert vaccination country data for guatemala
    ind_v = ind_v[::-1]
    for index, row in ind_v.iterrows():
        date1 = row['date']
        c.execute('SELECT * FROM Vaccinations_Per_Country WHERE country_code ="' + ind_code + '" AND date_collected ="' + str(date1)+ '"')
        result = c.fetchall()
        if len(result) == 0:
            sql = '''INSERT INTO Vaccinations_Per_Country (date_collected, first_vaccination_number, second_vaccination_number,  third_vaccination_number, country_code, source_id) VALUES (?, ?, ?, ?, ?, ?)'''
            c.execute(sql, (row["date"], toint(row["people_vaccinated"]), toint(row["people_fully_vaccinated"]), toint(row["total_boosters"]), ind_code, v_src))
        else:
            break
    conn.commit()

def update_china():
    # get country_code for china
    cn_code = get_country_code("China", c)
    
    conn = sqlite3.connect('sqlite_db')
    c = conn.cursor()
    
    #insert and get source id for china data
    cn_src_url = "https://github.com/BlankerL/DXY-COVID-19-Data"
    set_source(cn_src_url, c, conn)
    cn_src = get_source_id(cn_src_url, c)
    
    date1 = date.today()
    date1 = str(date1).replace("-", ".")
    link = "https://github.com/BlankerL/DXY-COVID-19-Data/releases/download/" + date1 + "/DXYArea.csv"
    cn_case = pd.read_csv(link)
    
    #insert country, region and distrct case data for china
    for index,row in cn_case.iterrows():
        region = row["countryEnglishName"]
        if region == "China":
            case = row["province_confirmedCount"]
            death = row["province_deadCount"]
            recover = row["province_curedCount"]
            date1 = row["updateTime"][:10]
            if row["provinceEnglishName"] == "China":
                c.execute('SELECT * FROM Cases_Per_Country WHERE country_code ="' + cn_code + '" AND date_collected ="' + str(date1)+ '"')
                result = c.fetchall()
                if len(result) == 0:
                    sql = '''INSERT INTO Cases_Per_Country (country_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                    c.execute(sql,(cn_code, date1, cn_src, death, case, recover))
                else:
                    break
            else:
                region_code = get_region_code(cn_code, region, c)
                c.execute('SELECT * FROM Cases_Per_Region WHERE region_code ="' + region_code + '" AND date_collected ="' + str(date1)+ '"')
                result = c.fetchall()
                if len(result) == 0: 
                    sql = '''INSERT INTO Cases_Per_Region (region_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                    c.execute(sql,(region_dict[region], date1, cn_src, death, case, recover))
                if (pd.isna(row["cityEnglishName"]) ==  False):
                    city = row["cityEnglishName"]
                    city_code = get_district_code(region_code, city, c)
                    c.execute('SELECT * FROM Cases_Per_District WHERE district_code ="' + city_code + '" AND date_collected ="' + str(date1)+ '"')
                    result = c.fetchall()
                    if len(result) == 0: 
                        sql = '''INSERT INTO Cases_Per_District (district_code, date_collected, source_id, death_numbers, case_numbers, recovery_numbers) VALUES (?, ?, ?, ?, ?, ?)'''
                        c.execute(sql,(city_dict[region][city], date1, cn_src, row["city_deadCount"], row["city_confirmedCount"], row["city_curedCount"]))
                    else:
                        break
    conn.commit()