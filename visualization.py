import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import json
from data_retrieval import *
from dash import Dash, dcc, html


pd.options.mode.chained_assignment = None

app = Dash(__name__)

colors = {"background": "#212A31", "text": "#D3D9D4", 'primary': '#2E3944', 'secondary': '#124E66', 'tertiary': '#748D92'}

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
      width=1280,
      height=800,
    )

    fig.update_layout(
      plot_bgcolor=colors['background'],
      paper_bgcolor=colors['background'],
      font_color=colors['text'],
      margin=dict(r=20, l=20, t=20, b=20),
    )

    fig.update_geos(
      showland=True,
      bgcolor=colors['background'],
    )

    app.layout = html.Div(id='html', className='parent', children=[
      html.H1(children='Vesicular Stomatitis Cases', style={
        'textAlign': 'center',
        'color': colors['text'],
        'margin-top': '0px',
      }),
    
      html.Div(children='Cases of Vesicular Stomatitis Within North America as a EWS', style={
        'textAlign': 'center',
        'color': colors['text']
      }),
    
      html.Div(style={'width': '80%', 'margin': 'auto'}, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'flex-start'}, children=[
          dcc.Checklist(
            id='my-checklist',
            options=[
              {'label': 'Order by Month?', 'value': 'Yes'},
            ],
            value=['Yes'],
            style={'color': colors['text']}
          ),
        ]),
      
        html.Div(style={'display': 'flex', 'justifyContent': 'flex-start'}, children=[
          dcc.Dropdown(
            id='my-dropdown',
            options=[
              {'label': 'January', 'value': 'OPT1'},
              {'label': 'February', 'value': 'OPT2'}
            ],
            value='OPT1'
          )
        ])
      ]),
    
      html.Div(
        dcc.Graph(
          id='choropleth',
          figure=fig
        ), style={'width': '80%', 'height': '80%', 'margin': 'auto'}
      ),
    
      html.Div(
        dcc.Slider(
          id='my-slider',
          min=0,
          max=20,
          step=0.5,
          value=10,
        ), style={'width': '80%', 'margin': 'auto'}
      )
    ])
    
    app.run(debug=True)