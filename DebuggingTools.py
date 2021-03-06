import pandas as pd
from datetime import timedelta

voyages = pd.read_csv('voyages.csv', parse_dates=["begin_date","end_date"])
diff = pd.DataFrame(abs(voyages['end_date']-voyages['begin_date']), columns=['delta'])
voyages = pd.concat([voyages,diff],axis=1)
voyages = voyages.where(voyages.delta < timedelta(days=7)).dropna()
voyages.to_csv('shorttrips.csv')

print(voyages.where(voyages['begin_port_id'] == voyages['end_port_id']).dropna())