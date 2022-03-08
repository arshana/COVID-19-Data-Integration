# Daily instructions:
# 1. Pull from the Github repo.
# 2. Run `python run_daily.py`.
# 3. Push to the Github repo.

# This script should be run once daily. 
# For safety's sake, and because data sources may not update at the same time everyday,
# the daily update scripts typically check that the previous two days of data have already been added to the db
# and add those days if they are missing.
# So you shouldn't need to worry about running this script at the same time every day 
# (and may be able to get away with missing a day).
# But that is just a precaution and is NOT guaranteed for future scripts
# so PLEASE RUN EVERYDAY!

# Ideal vision: This all gets moved to a server that runs the scripts automatically everyday.

from daily_data_scripts.daily_europe import daily_italy, daily_ukraine
from daily_data_scripts.daily_global import daily_jhu
from daily_data_scripts.daily_north_america import update_us, update_canada, update_guatemala
from daily_data_scripts.daily_south_america import update_brazil
from daily_data_scripts.daily_global_v import update_global_v
from daily_data_scripts.daily_asia import update_japan, update_korea, update_ina, update_china, update_india

daily_italy()
daily_ukraine()
daily_jhu()
update_brazil()
update_us()
update_canada()
update_guatemala()
update_japan()
update_korea()
update_ina()
update_china()
update_india()
update_global_v()