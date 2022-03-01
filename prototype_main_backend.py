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
                region_code BIGINT NOT NULL,
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
                hospitalization_numbers INT NULL,
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
                hospitalization_numbers INT NULL,
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
                hospitalization_numbers INT NULL,
                FOREIGN KEY (district_code) REFERENCES Districts(district_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_Country(
                first_vaccination_number BIGINT NOT NULL,
                second_vaccination_number BIGINT NOT NULL,
                third_vaccination_number BIGINT NOT NULL,
                country_code VARCHAR(2) PRIMARY KEY,
                source_id BIGINT NOT NULL,
                FOREIGN KEY (country_code) REFERENCES Countries(country_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_Region(
                first_vaccination_number BIGINT NOT NULL,
                second_vaccination_number BIGINT NOT NULL,
                third_vaccination_number BIGINT NOT NULL,
                region_code BIGINT PRIMARY KEY,
                source_id BIGINT NOT NULL,
                FOREIGN KEY (region_code) REFERENCES Regions(region_code),
                FOREIGN KEY (source_id) REFERENCES Sources(source_id)
            )
          ''')

c.execute('''
            CREATE TABLE Vaccinations_Per_District(
                first_vaccination_number BIGINT NOT NULL,
                second_vaccination_number BIGINT NOT NULL,
                third_vaccination_number BIGINT NOT NULL,
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

c.close()
from initial_data_scripts.init_europe import init_italy, init_ukraine
from initial_data_scripts.init_asia import init_japan, init_korea
from initial_data_scripts.init_global import init_jhu
