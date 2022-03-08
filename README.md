# COVID-19-Data-Integration
Code for integrating COVID-19 data from various sources. Includes subnational data.

## Backend

This covers everything related to setting up the database and getting data into the database.

### Database Structure

The database is in SQLite and is called sqlite_db.

When this database was designed, we intended to use SQLServer with Azure Data Factory, so we included the schema in data/OverallSchema.sql. However, due to time constraints, we switched to a SQLite implementation. So at this point, all tables were added through the run_main_initially.py file, which you can refer to for a better understanding of all the attributes of the tables. (This means that everything in the data folder is technically legacy code, but we haven't removed it in case it helps with an eventual migration to SQLServer.)

Here is an overview of the tables and their contents.

#### Countries

This table contains a list of country names (`country_name`) and the associated country codes (`country_code`). It was populated from country_countryCode.csv.

#### Regions

This table contains a list of region names (`region_name`), the associated region codes (`region_code`), and country code of the country the region is in (`country_code`). Regions are a 'sub-level' of countries. For example, the state Washington would be considered a region of the country United States. Regions can cover a variety of types of areas, including states and provinces and even cities. The only requirement is that it is one step down from a country. Take France as an example. If France's subnational data only included cities like Paris, Marseille, and Nice, rather than areas like Aquitaine or Normandy, then Paris would be considered a region for this database's purposes.

#### Districts

This table contains a list of district names (`district_name`), the associated district codes (`district_code`), and region code of the region the district is in (`region_code`). Districts are a 'sub-level' of regions the same way regions are a sub-level of countries. We decided to only include these three levels in our database because it seemed like a good average of all the data found. Some subnational data only goes to the region level. Very rarely, it might go deeper than the district level. But three levels covered most data without going so far beyond as to create confusion in maintaining the data.

#### Sources

This table contains a list of sources (`source_information`) associated with a generated `source_id`. `source_id` is often used as a foreign key in the data tables so that the user knows which source certain data came from. Also, if a source should every 'go bad,' it will be relatively straightforward to delete that source from the table.

Additionally, data is drawn from multiple sources. For example, the JHU data is used as the base source for the table since it contains global data on most countries. It contains death, case, and recovery numbers for Italy. However, the Italy data also contains death, case, and recovery numbers, along with some other data. (The JHU data appears superfluous in the case, but is maintained anyways, because the JHU source is considered more trustworthy than the source we use for the Italy data. Also, we know that JHU will continue to update, while we cannot say the same about the Italy source.) Both sets of data are in the same table. The `source_id` then becomes key in knowing which data the user actually wants to pull.

#### Cases_Per_Country

This table includes the `country_code` and the basic COVID-19 data: `source_id`, `date_collected`, `death_numbers`, `case_numbers`, `recovery_numbers`, and `hospitalization_numbers`. 

These numbers are daily values. Some sources had cumulative values originally. We calculated the daily values and inserted those into the table instead.

#### Cases_Per_Region

This is similar to `Cases_Per_Country`, but for regions.

#### Cases_Per_District

This is similar to `Cases_Per_Country`, but for districts.

#### Vaccinations_Per_Country

This table includes the `country_code` and data associated with vaccinations: `source_id`, `date_collected`, `first_vaccination_number`, `second_vaccination_number`, and `third_vaccination_number`. The vaccination numbers are basically the number of people who got their ith vaccination.

_Ivy, is this cumulative? or daily?_

#### Vaccinations_Per_Region

This is similar to `Vaccinations_Per_Country`, but for regions.

#### Vaccinations_Per_District

This is similar to `Vaccinations_Per_Country`, but for districts.

#### Population_Per_Country

This table includes the `country_code` and population of that country on a certain date: `date_collected` and `population_amount`.

The intention behind this table is to give users something to aggregate and manipulate data in other tables with. For instance, we number of deaths in the `Cases_Per_Country` table. But what if you wanted to know the percentage of deaths instead? This table would help with that. Unfortunately, this table is not exact and must be intentionally updated by a user. Population censuses are not taken often, so this data can't be used to determine exact percentages, only approximations. Regardless, we felt having a framework in place to help with such calculations would be useful.

#### Population_Per_Region

This is similar to `Population_Per_Country`, but for regions. Note that this population data will likely be more difficult to find than for countries.

#### Population_Per_District

This is similar to `Population_Per_Country`, but for districts. Note that this population data will likely be more difficult to find than for countries.

#### Age_Per_Country

This table is similar to `Cases_Per_Country` but has data divided based on ages as well. Also, unlike with `Cases_Per_Country`, different sources provided information in numbers or rates, so both versions are included in the table. The attributes include the `country_code` and the age-based COVID-19 data: `source_id`, `date_collected`, `age_group`, `death_number`, `case_number`, `recovery_number`, `hospitalization_number`, `death_rate`, `case_rate`, `recovery_rate`, and `hospitalization_rate`. 

Because age-based data is so comparatively rare, we included it in a separate table from the more general `Cases_Per_Country` table. The `age_group` attribute has data type VARCHAR(64). It is up to the person inserting the data to define what they want to put here and document it.

#### Age_Per_Region

This is similar to `Age_Per_Country`, but for regions.

#### Age_Per_District

This is similar to `Age_Per_Country`, but for districts.

### Initial Database Setup

The database is currently set up with SQLite and is stored in a Github repository. To initialize it, we ran `python run_main_initially.py`. This initialized the sqlite_db, added the tables, and inserted all the data in the data sources at the time of initialization.

This script should never be run again unless you are restarting the database from scratch. There is no guarantee the script will still be up-to-date or that it will account for any new edge cases that have developed over time.

### Daily Database Update

Run the following command daily: `python run_daily.py`.

This script will pull the new data from the data sources into the database. Be on the lookout for errors as new edge cases may develop over time!

run_daily.py contains imports functions from a variety of other python files. There is typically one function run for every still-current data source. The functions have links to their source that you may wish to access if you are using the data or if the functions need modifications to fit your needs.

## Frontend
