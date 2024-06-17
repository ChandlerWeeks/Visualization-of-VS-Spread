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
    
    
def get_fips():
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
  data['location'] = np.NaN

  for _, state in municipalities.iterrows():
    municipality_name = state['NAME']
    GEO_ID = state['GEO_ID']
    mask = (data['COUNTRY'] == 'MEX') & (data['COUNTY_MUNI'] == municipality_name.lower())
    #data['location'] = data['location'].astype(str)
    data.loc[mask, 'location'] = GEO_ID

  data['date'] = pd.to_datetime(data['date'])
  data['year'] = data['date'].dt.to_period('Y')
  data['month'] = data['date'].dt.month

  new_data = pd.DataFrame({
    'location': data['location'],
    'year': data['year'],
    'month': data['month'],
    'name': data['COUNTY_MUNI'].str.title(),
    'cases': 0
  })

  # drop na data
  new_data = new_data.dropna(subset=['name', 'location'])

  return new_data

def create_useable_US_dataframe(data):
  fips = get_fips()
  data['location'] = np.NaN  # Initialize a new column 'fips' with Null values

  for idx, row in fips.iterrows():
    mask = (data['STATE'] == str(row['state'])) & (data['COUNTY_MUNI'] == str(row['name']).lower()) & (data['COUNTRY'] == 'USA')
    #data['location'] = data['location'].astype(str)  
    data.loc[mask, 'location'] = row['fips'] 

  data = data.dropna(subset=['location'])  

  data['date'] = pd.to_datetime(data['date'])
  data['year'] = data['date'].dt.to_period('Y')
  data['month'] = data['date'].dt.month

  new_data = pd.DataFrame({
    'location': data['location'],
    'year': data['year'],
    'month': data['month'],
    'name': data['COUNTY_MUNI'].str.title(),
    'cases': 0
  })

  new_data = new_data.dropna(subset=['name', 'location'])

  return new_data

def aggregate_cases(data):
  data['cases'] = 1
  aggregaged_data = data.groupby(['location', 'name', 'year']).sum().reset_index()
  aggregaged_data = aggregaged_data.sort_values(by=['year', 'month'])
  aggregaged_data = aggregaged_data.dropna(subset=['location'])

  print(aggregaged_data)
  
  return aggregaged_data

# merges US counties and Mexican municipalities
def get_locations(data):
  us_data = create_useable_US_dataframe(data)
  mx_data = create_useable_MX_dataframe(data)

  data = pd.concat([us_data, mx_data])
  aggregated_cases = aggregate_cases(data)
  return aggregated_cases
