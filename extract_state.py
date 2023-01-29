import pandas as pd

state_to_extract = 'CO'
state_pickle_file = 'US/' + state_to_extract + '.pkl'
cities_pickle_file = 'US/' + state_to_extract + '_cities.pkl'

column_names = [
    'geonameid',
    'name',
    'asciiname',
    'alternatenames',
    'latitude',
    'longitude',
    'feature class',
    'feature code',
    'country code',
    'cc2',
    'admin1 code',
    'admin2 code',
    'admin3 code',
    'admin4 code',
    'population',
    'elevation',
    'dem',
    'timezone',
    'modification date',
]

us = pd.read_table('US/US.txt', names=column_names)
is_state = (us.loc[:, 'admin1 code'] == state_to_extract)
state = us.loc[is_state, :]
state.to_pickle(state_pickle_file)

# There are other features classes, e.g., mountains, roads, lakes
# See US/readme.txt
is_city = state.loc[:, 'feature class'] == 'P'
cities = state.loc[is_city, :]
cities.to_pickle(cities_pickle_file)
