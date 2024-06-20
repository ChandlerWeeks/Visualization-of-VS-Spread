import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import json
from data_retrieval import *

pd.options.mode.chained_assignment = None

#TODO: Convert the graph to a plotly go graph, add month filter and reenable the years filter, then publish
#TODO: https://plotly.com/python/choropleth-maps/

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
  geo = json.load(response)

with open('./data/municipalities.geojson', 'r', encoding='utf-8') as f:
  municipalities = json.load(f)


for feature in municipalities['features']:
  geo['features'].append(feature)

class data_visualizer:
  def __init__(self, df):
    self.convert_to_geo(df)
    self.display_months = False

  def convert_to_geo(self, data):
    #make date useable with no month or year
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
      scope="north america",
      hover_data={'location': False, 'name': True, 'cases': True},
      labels={'cases':'cases',},
      range_color=[self.df['cases'].min(), self.df['cases'].max()],
    )
  
    # Generate a dropdown item for each month
    months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]
    dropdown_items = []
    for i, month in enumerate(months):
      dropdown_items.append(
        dict(
          args=[{"transforms[0].value": i + 1}],  # The month number
          label=month,
          method="update"
        )
      )
  
    # Add a dropdown menu to the layout
    fig.update_layout(
      updatemenus=[
        dict(
          buttons=dropdown_items,
          direction="down",
          pad={"r": 10, "t": 10},
          showactive=True,
          x=0.1,
          xanchor="left",
          y=1.1,
          yanchor="top"
        )
      ],
      annotations=[
        dict(
          text="Select Month:",
          showarrow=False,
          x=0.025,  # Adjust these values to position the label
          y=1.083,  # Adjust these values to position the label
          xref="paper",
          yref="paper"
        )
      ]
    )
  
    # Add a filter transform to the data
    fig.update_layout(
      transforms=[
        dict(
          type='filter',
          target='date',  # The column to filter
          operation='month',  # Extract the month from the date
          value=1  # The initial month to display (January)
        )
      ]
    )
  
    fig.show()
