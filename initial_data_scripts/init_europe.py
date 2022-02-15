import pandas as pd
import datetime

# Use this for European countries only. Other countries appear to be either unreliable or have a lot of holes in their data.
def init_jrc():
    df = pd.read_csv('https://raw.githubusercontent.com/ec-jrc/COVID-19/master/data-by-region/jrc-covid-19-all-days-by-regions.csv', error_bad_lines=False)

# JRC includes Germany data, but not the same subsets
def init_germany():
    pass

# JRC includes UK data, but not the same subsets
def init_uk():
    pass

# JRC includes Italy data, but not the same subsets
def init_italy():
    df_total = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_total.csv', error_bad_lines=False)
    df_region = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_region.csv', error_bad_lines=False)
    df_subregion = pd.read_csv('https://raw.githubusercontent.com/RamiKrispin/covid19Italy/master/csv/italy_province.csv', error_bad_lines=False)

# Starts on 3/3/2020.
def init_ukraine():
    dt = datetime.datetime.today()
    for year in range(2020, int(dt.year) + 1):
        start_month = 1
        if (year == 2020):
            start_month = 3
        end_month = 13
        if (year == int(dt.year)):
            end_month = int(dt.month) + 1
        for month in range(start_month, end_month):
            start_day = 1
            if (year == 2020 and start_month == 3):
                start_day = 3
            end_day = 32
            if (year == int(dt.year) and month == int(dt.month)):
                end_day = dt.day + 1
            for day in range(start_day, end_day):
                if (isValidDate(year, month, day)):
                    csv_name = 'https://raw.githubusercontent.com/dmytro-derkach/covid-19-ukraine/master/daily_reports/' + ('0' if month < 10 else '')  + str(month) + '-' + ('0' if day < 10 else '') + str(day) + '-' + str(year) + '.csv'
                    try:
                        df = pd.read_csv(csv_name, error_bad_lines=False)
                    except:
                        print('Ukraine init failed on ' + csv_name)

def init_france():
    pass

def isValidDate(year, month, day):
    isValidDate = True
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        isValidDate = False
    return isValidDate

