# Game focused on CO cities
# Forget highways for now
# Aircraft for charter?
# Helicopter, then Cessna, etc.
# Demand based on population
# Profit based on capacity and distance
# Fuel cost based on distance/aircraft type
# Fuel cost based on city/random
# Rent or buy hangar space in each city
# Hire or contract mechanics in each city

# Run extract_state.py first to create US/CO.pkl and US/CO_cities.pkl

import pandas as pd

cities = pd.read_pickle('US/CO_cities.pkl')

# Useful columns: name, latitude, longitude, population, elevation
# cities.columns

cities.loc[:, ['name', 'asciiname', 'alternatenames']]
cities.loc[:, ['dem', 'elevation']]
