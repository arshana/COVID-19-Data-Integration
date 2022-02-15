import pandas as pd
import datetime

# Use this for European countries only. Other countries appear to be either unreliable or have a lot of holes in their data.
def init_jrc():
    df = pd.read_csv('https://raw.githubusercontent.com/ec-jrc/COVID-19/master/data-by-region/jrc-covid-19-regions-latest.csv', error_bad_lines=False)
    
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

# Updates daily. Check for both yesterday's and today's data to make sure they are both gotten regardless of when the source is updated
def init_ukraine():
    dt = datetime.datetime.today()
    csv_name_today = 'https://raw.githubusercontent.com/dmytro-derkach/covid-19-ukraine/master/daily_reports/' + ('0' if dt.month < 10 else '')  + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day) + '-' + str(dt.year) + '.csv'
    dt -= datetime.timedelta(days=1)
    csv_name_yesterday = 'https://raw.githubusercontent.com/dmytro-derkach/covid-19-ukraine/master/daily_reports/' + ('0' if dt.month < 10 else '')  + str(dt.month) + '-' + ('0' if dt.day < 10 else '') + str(dt.day) + '-' + str(dt.year) + '.csv'
    try:
        df_yesterday = pd.read_csv(csv_name_yesterday, error_bad_lines=False)
    except:
        pass
    try:
        df_today = pd.read_csv(csv_name_today, error_bad_lines=False)
    except:
        pass

def init_france():
    pass
