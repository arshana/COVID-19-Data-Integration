-- each country code and name are unique 
-- no nulls
-- country codes are used in the rest of the tables as keys
CREATE TABLE Countries(
    country_code VARCHAR(2) PRIMARY KEY,
    country_name VARCHAR(128) UNIQUE NOT NULL
);

-- encaptures data about the region
-- longittude and latitude specify certain part of the region
CREATE TABLE Regions(
    region_code BIGINT IDENTITY(1, 1) PRIMARY KEY,
    region_name VARCHAR(128) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    longitude FLOAT NULL,
    latitude FLOAT NULL,
    FOREIGN KEY (country_code) REFERENCES Countries(country_code)
);

-- information of the location of the district
-- longitude and latitude specify certain part of the district
CREATE TABLE Districts(
    district_code BIGINT IDENTITY(1, 1) PRIMARY KEY,
    district_name VARCHAR(128) NOT NULL,
    region_code BIGINT NOT NULL,
    longitude FLOAT NULL,
    latitude FLOAT NULL,
    FOREIGN KEY (region_code) REFERENCES Regions(region_code)
);

-- source ID to source information
-- source ID is autogenerated
-- source info is unique
CREATE TABLE Sources(
    source_id BIGINT IDENTITY(1, 1) PRIMARY KEY,
    source_information VARCHAR(256) UNIQUE NOT NULL
);

-- information on cases, recovery numbers, and deaths
-- per countries
CREATE TABLE Cases_Per_Country(
    country_code VARCHAR(2),
    date_collected DATETIME2 NOT NULL,
    source_id BIGINT NOT NULL,
    death_numbers INT NULL,
    case_numbers INT NULL,
    recovery_numbers INT NULL,
    hospitalization_numbers INT NULL,
    FOREIGN KEY (country_code) REFERENCES Countries(country_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- information on cases, recovery numbers, and deaths
-- per region
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
);

-- information on cases, recovery numbers, and deaths
-- per district
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
);

-- keeps track of vaccinations per Country
CREATE TABLE Vaccinations_Per_Country(
    first_vaccination_number BIGINT NOT NULL,
    second_vaccination_number BIGINT NOT NULL,
    third_vaccination_number BIGINT NOT NULL,
    country_code VARCHAR(2) ,
    source_id BIGINT NOT NULL,
    FOREIGN KEY (country_code) REFERENCES Countries(country_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- keeps track of vaccinations per Region
CREATE TABLE Vaccinations_Per_Region(
    first_vaccination_number BIGINT NOT NULL,
    second_vaccination_number BIGINT NOT NULL,
    third_vaccination_number BIGINT NOT NULL,
    region_code BIGINT,
    source_id BIGINT NOT NULL,
    FOREIGN KEY (region_code) REFERENCES Regions(region_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- keeps track of vaccinations per District
CREATE TABLE Vaccinations_Per_District(
    first_vaccination_number BIGINT NOT NULL,
    second_vaccination_number BIGINT NOT NULL,
    third_vaccination_number BIGINT NOT NULL,
    district_code BIGINT,
    source_id BIGINT NOT NULL,
    FOREIGN KEY (district_code) REFERENCES Districts(district_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- keeps track of strain data per country
CREATE TABLE Strains_Per_Country(
    country_code VARCHAR(2) PRIMARY KEY,
    source_id BIGINT NOT NULL,
    alpha_rate INT NULL,
    beta_rate INT NULL,
    gamma_rate INT NULL,
    delta_rate INT NULL,
    omicron_rate INT NULL,
    FOREIGN KEY (country_code) REFERENCES Countries(country_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- keeps track of strain data per region
CREATE TABLE Strains_Per_Region(
    region_code BIGINT PRIMARY KEY,
    source_id INT NOT NULL,
    alpha_rate INT NULL,
    beta_rate INT NULL,
    gamma_rate INT NULL,
    delta_rate INT NULL,
    omicron_rate INT NULL,
    FOREIGN KEY (region_code) REFERENCES Regions(region_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- keeps track of strain data per district
CREATE TABLE Strains_Per_District(
    district_code BIGINT PRIMARY KEY,
    source_id INT NOT NULL,
    alpha_rate INT NULL,
    beta_rate INT NULL,
    gamma_rate INT NULL,
    delta_rate INT NULL,
    omicron_rate INT NULL,
    FOREIGN KEY (district_code) REFERENCES Districts(district_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- age related data on covid per country
CREATE TABLE Age_Per_Country(
    date_collected DATETIME2 NOT NULL,
    country_id VARCHAR(2),
    source_id BIGINT NOT NULL,
    age_group VARCHAR(64) NOT NULL,
    case_number INT NULL,
    recovery_number INT NULL,
    hospitalization_number INT NULL,
    death_number INT NULL,
    case_rate INT NULL,
    recovery_rate INT NULL,
    hospitalization_rate INT NULL,
    death_rate INT NULL,
    FOREIGN KEY (country_id) REFERENCES Countries(country_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- age related data on covid per region
CREATE TABLE Age_Per_Region(
    date_collected DATETIME2 NOT NULL,
    region_id BIGINT,
    source_id BIGINT NOT NULL,
    age_group VARCHAR(64) NOT NULL,
    case_number INT NULL,
    recovery_number INT NULL,
    hospitalization_number INT NULL,
    death_number INT NULL,
    case_rate INT NULL,
    recovery_rate INT NULL,
    hospitalization_rate INT NULL,
    death_rate INT NULL,
    FOREIGN KEY (region_id) REFERENCES Regions(region_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- age related data on covid per district
CREATE TABLE Age_Per_District(
    date_collected DATETIME2 NOT NULL,
    district_id BIGINT,
    source_id BIGINT NOT NULL,
    age_group VARCHAR(64) NOT NULL,
    case_number INT NULL,
    recovery_number INT NULL,
    hospitalization_number INT NULL,
    death_number INT NULL,
    case_rate INT NULL,
    recovery_rate INT NULL,
    hospitalization_rate INT NULL,
    death_rate INT NULL,
    FOREIGN KEY (district_id) REFERENCES Districts(district_code),
    FOREIGN KEY (source_id) REFERENCES Sources(source_id)
);

-- population per country on a given date
CREATE TABLE Population_Per_Country(
    country_code VARCHAR(2) PRIMARY KEY,
    population_amount BIGINT NOT NULL,
    date_collected DATETIME2 NOT NULL,
    FOREIGN KEY (country_code) REFERENCES Countries(country_code)
);

-- population per region on a given date
CREATE TABLE Population_Per_Region(
    region_code BIGINT PRIMARY KEY,
    population_amount BIGINT NOT NULL,
    date_collected DATETIME2 NOT NULL,
    FOREIGN KEY (region_code) REFERENCES Regions(region_code)
);

-- population per district on a given date
CREATE TABLE Population_Per_District(
    district_code BIGINT PRIMARY KEY,
    population_amount BIGINT NOT NULL,
    date_collected DATETIME2 NOT NULL,
    FOREIGN KEY (district_code) REFERENCES Districts(district_code)
);