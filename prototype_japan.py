import sqlite3
import pandas as pd

conn = sqlite3.connect('prototype_db')
c = conn.cursor()

c.execute('''
            CREATE TABLE Countries(
            country_code VARCHAR(2) PRIMARY KEY,
            country_name VARCHAR(128) UNIQUE NOT NULL
            )
          ''')
c.execute('''
            CREATE TABLE Regions(
            region_code INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            region_name VARCHAR(128) NOT NULL,
            country_code VARCHAR(2) NOT NULL,
            longitude FLOAT NULL,
            latitude FLOAT NULL,
            FOREIGN KEY (country_code) REFERENCES Countries(country_code)
            )
          ''')

c.execute('''
            CREATE TABLE Districts(
                district_code INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                district_name VARCHAR(128) NOT NULL,
                region_code VARCHAR(5) NOT NULL,
                longitude FLOAT NULL,
                latitude FLOAT NULL,
                FOREIGN KEY (region_code) REFERENCES Regions(region_code)
            )
          ''')

c.execute('''
            CREATE TABLE Sources(
                source_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                source_information VARCHAR(256) UNIQUE NOT NULL
            )
          ''')

c.execute('''
            CREATE TABLE Cases_Per_Country(
                country_code VARCHAR(2) ,
                date_collected DATETIME2 NOT NULL,
                source_id BIGINT NOT NULL,
                death_numbers INT NULL,
                case_numbers INT NULL,
                recovery_numbers INT NULL,
                FOREIGN KEY (country_code) REFERENCES Countries(country_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Cases_Per_Region(
                region_code BIGINT,
                date_collected DATETIME2 NOT NULL,
                source_id BIGINT NOT NULL,
                death_numbers INT NULL,
                case_numbers INT NULL,
                recovery_numbers INT NULL,
                FOREIGN KEY (region_code) REFERENCES Regions(region_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Cases_Per_District(
                district_code BIGINT,
                date_collected DATETIME2 NOT NULL,
                source_id BIGINT NOT NULL,
                death_numbers INT NULL,
                case_numbers INT NULL,
                recovery_numbers INT NULL,
                FOREIGN KEY (district_code) REFERENCES Districts(district_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_Country(
                vaccination_rate FLOAT NOT NULL,
                country_code VARCHAR(2) PRIMARY KEY,
                source_id BIGINT NOT NULL,
                FOREIGN KEY (country_code) REFERENCES Countries(country_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_Region(
                vaccination_rate FLOAT NOT NULL,
                region_code BIGINT PRIMARY KEY,
                source_id BIGINT NOT NULL,
                FOREIGN KEY (region_code) REFERENCES Regions(region_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_District(
                vaccination_rate FLOAT NOT NULL,
                district_code BIGINT PRIMARY KEY,
                source_id BIGINT NOT NULL,
                FOREIGN KEY (district_code) REFERENCES Districts(district_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''CREATE TABLE Population_Per_Country(
            country_code VARCHAR(2) PRIMARY KEY,
            population_amount BIGINT NOT NULL,
            date_collected DATETIME2 NOT NULL,
            FOREIGN KEY (country_code) REFERENCES Countries(country_code)
        ); 
        ''')

c.execute('''CREATE TABLE Population_Per_Region(
            region_code BIGINT PRIMARY KEY,
            population_amount BIGINT NOT NULL,
            date_collected DATETIME2 NOT NULL,
            FOREIGN KEY (region_code) REFERENCES Regions(region_code)
        );
         ''')

c.execute('''CREATE TABLE Population_Per_District(
            district_code BIGINT PRIMARY KEY,
            population_amount BIGINT NOT NULL,
            date_collected DATETIME2 NOT NULL,
            FOREIGN KEY (district_code) REFERENCES Districts(district_code)
        ); 
        ''')
                  
conn.commit()

#insert country_countryCode table
countries = pd.read_csv('country_countryCode.csv')
countries = countries.rename(columns={"Name": "country_name", "Code": "country_code"})
countries.to_sql('Countries',con=conn, if_exists = 'append', index=False)

# get country_code for Japan
c.execute("SELECT country_code from Countries where country_name = 'Japan'")
result = c.fetchall()
japan_code = result[0][0]
print(result[0][0])

# insert and get source id for japan source1 
c.execute('''INSERT INTO Sources (source_information)
VALUES('https://covid19.mhlw.go.jp/en/');''')
conn.commit()
c.execute("SELECT source_id from Sources where source_information = 'https://covid19.mhlw.go.jp/en/'")
result = c.fetchall()
japan_source1 = result[0][0]

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
    c.execute(sql,(japan_code, row.Date, japan_source1, row.ALL_y, row.ALL_x))
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
        c.execute(sql,(city[0], row['Date'], japan_source1, row[city[2]], row[city[1]]))
conn.commit()

#insert and get source id for Japan vaccianation data
c.execute('''INSERT INTO Sources (source_information)
VALUES('https://www.kantei.go.jp/jp/headline/kansensho/vaccine.html');''')
conn.commit()
c.execute("SELECT source_id from Sources where source_information = 'https://www.kantei.go.jp/jp/headline/kansensho/vaccine.html'")
result = c.fetchall()
japan_source2 = result[0][0]

#install translator
pip install google_trans_new
from google_trans_new import google_translator  
translator = google_translator()  

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
        c.execute(sql,(rate, japan_code, japan_source2))
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
        c.execute(sql,(rate, region_dict[city], japan_source2))
        sql = '''INSERT INTO Population_Per_Region (region_code, population_amount, date_collected) VALUES (?, ?, ?)'''
        c.execute(sql,(region_dict[city], row[12], date.today()))
conn.commit()