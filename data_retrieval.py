import pandas as pd
import geopandas as gpd
import numpy as np
import json

class data_reciever:
  def __init__(self):
    self.file = './data/vsv_county_noPII.csv'
    self.recieve_data()

  def recieve_data(self):
    self.data = pd.read_csv(self.file)
    
  def filter_rows(self, year):
    return self.data[self.data['ONSET_YEAR'] == year]
    
def get_fip():
  fips = pd.read_csv('./data/state_and_county_fips_master.csv', dtype={'fips': str})
  return fips

def get_mexican_municipalities():
  municipalities = pd.read_csv('./data/mexico.csv')
  return municipalities

def get_mexican_states():
  states = pd.read_csv('./data/MEX_states.csv')
  return states

def create_useable_MX_dataframe(data):
  municipalities = get_mexican_municipalities()
  states = get_mexican_states()
  data['location'] = np.nan 

  state_mapping = states.set_index('State')['Conv'].to_dict()

  for _, state in municipalities.iterrows():
    state_name = state['STATE']
    municipalities_name = state['NAME']
    CVEGEO = state['GEO_ID']
    mask = (data['COUNTRY'] == 'MEX') & (data['COUNTY_MUNI'] == municipalities_name.lower())
    data['location'] = data['location'].astype(str)
    data.loc[mask, 'location'] = CVEGEO

  data['date'] = pd.to_datetime(data['date'])
  data['month_year'] = data['date'].dt.to_period('Y')

  new_data = pd.DataFrame({
    'location': data['location'],
    'date': data['month_year'],
    'Name': data['COUNTY_MUNI'].str.title(),
    'cases': 0
  })

  # drop na data
  new_data = new_data.dropna(subset=['Name'])
  new_data = new_data[~new_data.applymap(lambda x: x == 'nan').any(axis=1)]

  return new_data

def create_useable_US_dataframe(data):
  fips = get_fip()
  data['location'] = np.nan  # Initialize a new column 'fips' with Null values

  for idx, row in fips.iterrows():
    mask = (data['STATE'] == str(row['state'])) & (data['COUNTY_MUNI'] == str(row['name']).lower()) & (data['COUNTRY'] == 'USA')
    data['location'] = data['location'].astype(str)  
    data.loc[mask, 'location'] = row['fips'] 

  data = data.dropna(subset=['location'])  

  data['date'] = pd.to_datetime(data['date'])
  data['month_year'] = data['date'].dt.to_period('Y')

  new_data = pd.DataFrame({
    'location': data['location'],
    'date': data['month_year'],
    'Name': data['COUNTY_MUNI'].str.title(),
    'cases': 0
  })

  new_data = new_data.dropna(subset=['Name'])
  new_data = new_data[~new_data.applymap(lambda x: x == 'nan').any(axis=1)]

  return new_data

def aggregate_cases(data):
  data['cases'] = 1
  aggregaged_data = data.groupby(['location', 'date', 'Name']).sum().reset_index()
  return aggregaged_data.sort_values(by=['date'])

# merges US counties and Mexican municipalities
def get_locations(data):
  us_data = create_useable_US_dataframe(data)
  mx_data = create_useable_MX_dataframe(data)

  data = pd.concat([us_data, mx_data])
  data.dropna(subset=['Name'], inplace=True)
  aggregated_cases = aggregate_cases(data)

  print(aggregated_cases)

  return aggregated_cases
