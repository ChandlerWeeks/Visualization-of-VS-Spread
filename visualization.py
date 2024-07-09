import plotly.express as px
import pandas as pd
from data_retrieval import *
from dash import Dash, dcc, html, Input, Output, callback
#from jupyter_dash import JupyterDash

pd.options.mode.chained_assignment = None

app = Dash(__name__)
#app = JupyterDash(__name__)

#colors for css styling
colors = {"background": "#212A31", "text": "#D3D9D4", 'primary': '#2E3944', 'secondary': '#124E66', 'tertiary': '#748D92'}

geo = get_geo()

#TODO: add extra visualization, probably a bar graph with selection regions during selected timeframe
#TODO: experiment with color, particuarly rivers, lakes, ocean, cases, etc
class data_visualizer:
  def __init__(self, df):
    self.convert_to_geo(df)
    self.display_months = False

  # setup some data through pandas
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


  def get_unique_years(self):
    values = list(set(int(period.year) for period in self.df['year']))
    values.sort()
    return values


  def plot_data(self):
    fig = px.choropleth(
      filter_by_year(self.df, '1907'),
      geojson=geo,
      locations='location',
      color='cases',
      scope="north america",
      hover_data={'location': False, 'name': True, 'cases': True},
      labels={'cases':'cases',},
      #color_continuous_scale='reds', #TODO: experiment with color,
      width=1400,
      height=800,
    )

    fig.update_layout(
      dragmode='lasso',
      plot_bgcolor=colors['background'],
      paper_bgcolor=colors['background'],
      font_color=colors['text'],
      margin=dict(r=20, l=20, t=20, b=20),
    )

    fig.update_geos(
      showland=True,
      bgcolor=colors['background'],
    )

    unique_years = self.get_unique_years()

    app.layout = html.Div(id='html', className='parent', children=[
      html.H1(children='Vesicular Stomatitis Cases', style={
        'textAlign': 'center',
        'color': colors['text'],
        'padding-top': '12px',
        'margin-top': '0px',
        'font-size': '2.5em'
      }),
    
      html.Div(children='Cases of Vesicular Stomatitis Within North America as a EWS', style={
        'textAlign': 'center',
        'color': colors['text'],
        'font-size': '1.25em'
      }),

      html.Div(className='dropdown-box', children=[
        dcc.Dropdown(
          id='month-dropdown',
          options=[
            {'label': 'January', 'value': '1'},
            {'label': 'February', 'value': '2'},
            {'label': 'March', 'value': '3'},
            {'label': 'April', 'value': '4'},
            {'label': 'May', 'value': '5'},
            {'label': 'June', 'value': '6'},
            {'label': 'July', 'value': '7'},
            {'label': 'August', 'value': '8'},
            {'label': 'September', 'value': '9'},
            {'label': 'October', 'value': '10'},
            {'label': 'November', 'value': '11'},
            {'label': 'December', 'value': '12'},
          ],
          multi=True,
          className='dropdown',
        )
      ]),
    
      html.Div(
        dcc.Graph(
          id='choropleth',
          figure=fig
        ), style={'width': '75%', 'height': '75%', 'margin': 'auto', 'margin-top': '16px'}
      ),
    
      html.Div(
        dcc.Slider(
          id='year-slider',
          min=int(unique_years[0]),
          max=int(unique_years[-1]),
          step=1,
          value=int(unique_years[0]),
          marks = {i: {'label': str(i), 'style': {'color': 'text-color', 'font-size': 16}} for i in range(1910, 2021, 10)},
          tooltip={
            'always_visible': True,
            'style': {'color': colors['text'], 'fontSize': '24px'}
          }
        ), className='year-slider'
      )
    ])

    
    #TODO: add callback to adjust month
    @callback(
      Output(component_id='choropleth', component_property='figure'),
      [Input(component_id='year-slider', component_property='value'),
       Input(component_id='month-dropdown', component_property='value')]
    )


    def update_graph(selected_year, selected_months):
      if selected_months is None or selected_months == []:
        filtered_df = filter_by_year(self.df, str(selected_year))
      else:
        filtered_df = filter_by_months(self.df, str(selected_year), selected_months)

      print(filtered_df)
      fig = px.choropleth(
        filtered_df,
        geojson=geo,
        locations='location',
        color='cases',
        scope="north america",
        hover_data={'location': False, 'name': True, 'cases': True},
        labels={'cases':'cases',},
        #color_continuous_scale='reds', 
        width=1400,
        height=800,
      )

      fig.update_layout(
        dragmode='lasso',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        margin=dict(r=20, l=20, t=20, b=20),
      )

      fig.update_geos(
        showland=True,
        bgcolor=colors['background'],
      )

      return fig
    
    app.run(debug=True)
    #app.runserver(debug=True)