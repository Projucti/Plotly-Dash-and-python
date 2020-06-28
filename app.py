# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import base64
import json
import plotly.graph_objects as go
import numpy as np
import copy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# -- data -- #
# URL of geojson
# with urlopen('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson') as response:
with open('./data/countries.geojson') as response:
    countries = json.load(response)

df = pd.read_csv('./data/wdata.csv')
df = df[df.location != "World"]
print(list(df.columns))

logo_filename = './data/logo_upb.png'
encoded_image = base64.b64encode(open(logo_filename, 'rb').read())

# -- data end -- #

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

layout = dict(
    autosize=True,
    height=500,
    font=dict(color=colors['text']),
    titlefont=dict(color=colors['text'], size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    legend=dict(font=dict(size=10), orientation='h'),
    mapbox=dict(
        style="light",
        center=dict(
            lon=-73.91251,
            lat=40.7342
        ),
        zoom=10,
    )
)

# Creating layouts
layout_right = copy.deepcopy(layout)
layout_right['height'] = 300
layout_right['margin-top'] = '20'
layout_right['font-size'] = '12'

# Create figure
fig = go.Figure()

# dropdown, button

df_location=df.copy()
df_location=df_location['location']
locations = list(np.unique(df_location))
dff = df.copy()
dff = dff[dff['location'] == 'World']
group = ['All']
group = group + ['Low', 'Medium', 'High', 'Very High']
group_class = [{'label': str(item),
                      'value': str(item)}
                     for item in group]


# components style
# ------------ #

fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])

fig = px.choropleth_mapbox(df, geojson=countries, locations='iso_code', featureidkey="properties.ISO_A3",
                           color='total_cases',
                           color_continuous_scale="YlOrRd",
                           # range_color=(0, 1500000),
                           mapbox_style="carto-positron",
                           zoom=1.5, center={"lat": 25, "lon": 0},
                           opacity=0.6,
                           labels={'total_cases': 'Number of total cases'}
                           )
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


# app layout
app.layout = html.Div([
    # Title and Logo
    html.Div(
        [
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                className='two columns',
                style={
                    'height': '20%',
                    'width': '20%',
                    'float': 'left',
                    'position': 'relative',
                    'padding-top': 10,
                    'padding-right': 0
                },
            ),
            html.H1(
                'Covid-19 Information Center',
                style={'font-family': 'Helvetica',
                       "margin-top": "50",
                       "margin-bottom": "0"},
                className='eight columns',
            ),
            html.P(
                # some spaces
                '     ',
                style={'font-family': 'Helvetica',
                       "font-size": "120%",
                       "width": "80%"},
                className='eight columns',
            ),
        ],
        className='row'
    ),
    # Selection
    html.Div(
        [
            html.Div(
                [
                    html.P('Choose Dataset:'),
                    dcc.Checklist(
                            id = 'Dataset',
                            options=[
                                {'label': 'World', 'value': 'world-data'},
                                {'label': 'Germany', 'value': 'rki-data'},
                            ],
                            value=['World', 'Germany'],
                            labelStyle={'display': 'inline-block'}
                    ),
                ],
                className='three columns',
                style={'margin-top': '10'}
            ),
            html.Div(
                [
                    html.P('Choose Country:'),
                    dcc.Dropdown(id='loc_dropdown',
                        options=[
                        {'label': location, 'value': location} for location in locations
                        ],
                        multi=False,
                        value='Country',
                    ),
                ],
                className='two columns',
                style={'margin-top': '10'}
             ), 
            html.Div(
                [
                    html.P('Select metric for bar chart:'),
                    dcc.Dropdown(
                        id='metric_bar_chart',
                        options= group_class,
                        multi=False,
                        value='Select'
                    )
                ],
                className='two columns',
                style={'margin-top': '10'}
            ),
            html.Div(
                [
                    html.P('Select metric for line chart:'),
                    dcc.Dropdown(
                        id='metric_line_chart',
                        options= group_class,
                        multi=False,
                        value='Select'
                    )
                ],
                className='two columns',
                style={'margin-top': '10'}
            )
        ],
        className='row'
    ),
    # map, bar and line chart
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(id='world-map',
                            style={'margin-top': '20'})
                ], className = "six columns"
            ),
            html.Div(
                [
                    # bar chart
                    dcc.Graph(id='bar-graph',
                        figure={
                            'data': [
                                {'x': dff['date'], 'y':dff['new_cases'] , 'range_x': ['2020-02-02','2020-07-31'], 'type': 'bar', 'name': 'new cases'},
                            ],
                            'layout': {'title': 'Daily new cases for World'},
                        },
                        style={'font-family': 'Helvetica',
                       "font-size": "120%",
                       "width": "80%"},
                    ),
                ], className="three columns"
            ),
            html.Div(
                [
                    # line chart
                    dcc.Graph(id='line-graph',
                        figure={
                            'data': [
                                {'x': dff['date'], 'y':dff['total_cases'] , 'range_x': ['2020-02-02','2020-07-31'], 'type': 'line', 'name': 'total cases'}
                            ],
                        'layout': {'title': 'Total Coronavirus cases for World'},
                        },
                        style=layout_right,
                    ),
                ], className="three columns"
            ),
            html.Div(
                [
                    dcc.Graph(id="graph-chart")
                ], className="twelve columns"
            ),
        ], className="row"
    )
], className='ten columns offset-by-one')
# -- end of components -- #

# ---------- #

# callbacks and functions
# ---------- # 

if __name__ == '__main__':
    app.run_server(debug=True)
