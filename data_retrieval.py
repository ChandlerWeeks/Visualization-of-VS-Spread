import pandas as pd
import geopandas as gpd
import calendar

class data_reciever:
  def __init__(self):
    self.file = './data/vsv_county_noPII.csv'
    self.recieve_data()

  def recieve_data(self):
    self.data = pd.read_csv(self.file)
    
    
def get_fips():
  fips = pd.read_csv('./data/state_and_county_fips_master.csv', dtype={'fips': str})
  return fips

def get_municipality_ids():
  municipalities = pd.read_csv('./data/mexico.csv')
  return municipalities

def create_useable_mx_dataframe(data):
  municipalities = get_municipality_ids()
  data['location'] = None

  for _, state in municipalities.iterrows():
    municipality_name = state['NAME']
    GEO_ID = state['GEO_ID']
    mask = (data['COUNTRY'] == 'MEX') & (data['COUNTY_MUNI'] == municipality_name.lower())
    data.loc[mask, 'location'] = GEO_ID

  data['date'] = pd.to_datetime(data['date'])
  data['year'] = data['date'].dt.to_period('Y')
  month_dict = {i: calendar.month_name[i] for i in range(1, 13)}
  data['month'] = data['date'].dt.month.map(month_dict)

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

def create_useable_us_dataframe(data):
  fips = get_fips()
  data['location'] = None  # Initialize a new column 'fips' with Null values

  for idx, row in fips.iterrows():
    mask = (data['STATE'] == str(row['state'])) & (data['COUNTY_MUNI'] == str(row['name']).lower()) & (data['COUNTRY'] == 'USA')
    data.loc[mask, 'location'] = row['fips'] 

  data = data.dropna(subset=['location'])  

  data['date'] = pd.to_datetime(data['date'])
  data['year'] = data['date'].dt.to_period('Y')
  month_dict = {i: calendar.month_name[i] for i in range(1, 13)}
  data['month'] = data['date'].dt.month.map(month_dict)

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
  aggregated_data = data.groupby(['location', 'year', 'month']).sum().reset_index()
  aggregated_data = aggregated_data.sort_values(by=['year', 'month'])
  aggregated_data = aggregated_data.dropna(subset=['location'])
  
  return aggregated_data

# merges US counties and Mexican municipalities
def get_locations(data):
  us_data = create_useable_us_dataframe(data)
  mx_data = create_useable_mx_dataframe(data)

  data = pd.concat([us_data, mx_data])
  aggregated_cases = aggregate_cases(data)

  print(aggregated_cases)
  return aggregated_cases
