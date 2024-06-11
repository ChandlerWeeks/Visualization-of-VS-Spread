import plotly.express as px
import geopandas as gpd
import pandas as pd
from urllib.request import urlopen
import json
from data_retrieval import *

pd.options.mode.chained_assignment = None

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
  geo = json.load(response)

with open('./data/municipalities.geojson', 'r', encoding='utf-8') as f:
  municipalities = json.load(f)


for feature in municipalities['features']:
  geo['features'].append(feature)

class data_visualizer:
  def __init__(self, df):
    self.convert_to_geo(df)

  def convert_to_geo(self, data):
    data['ONSET_MONTH'] = data['ONSET_MONTH'].fillna(1)
    data.loc[:, 'ONSET_DAY'] = data['ONSET_DAY'].fillna(1)

    date_data = data[['ONSET_YEAR', 'ONSET_MONTH', 'ONSET_DAY']].copy()
    date_data = date_data.rename(columns={
        'ONSET_YEAR': 'year',
        'ONSET_MONTH': 'month',
        'ONSET_DAY': 'day'
    })

    date_data['date'] = pd.to_datetime(date_data, errors='coerce')
    data['date'] = date_data['date']
    data = data.drop(columns=['ONSET_YEAR', 'ONSET_MONTH', 'ONSET_DAY'])

    self.df = get_locations(data)

  def plot_data(self):
    fig = px.choropleth(
              self.df,
              geojson=geo,
              locations='location',
              color='cases',
              #color_continuous_scale="Reds",
              scope="north america",
              hover_data={'location': False, 'Name': True, 'cases': True},
              labels={'cases':'cases',},
              #animation_frame='date',
              range_color=[self.df['cases'].min(), self.df['cases'].max()],
              )

    fig.update_layout(
      title='Vesicular Stomatitis Cases By Year',
      title_x=0.5,
      title_font=dict(size=36, color='black', family='Arial, sans-serif', weight='bold'),
      #margin={"r":0,"t":30,"l":0,"b":0}
      )

    fig.show()

