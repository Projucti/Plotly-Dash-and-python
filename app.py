# -*- coding: utf-8 -*-
import base64
import copy
import json
import os
import time
import urllib.request
# the following two are necessary, if date is chosen using a calendar:
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from preprocessing import preprocess_and_laod_germany_data
from dash.dependencies import Input, Output

# import re

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = ['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

##### GERMANY #####
ts = lambda dt64: datetime.utcfromtimestamp((dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))

for _, _, files in os.walk("./data", topdown=False):
    if 'data_germany.pickle' in (files):
        df_germany = pd.read_pickle('./data/data_germany.pickle').drop_duplicates('ObjectId')
    else:
        df_germany = preprocess_and_laod_germany_data().drop_duplicates('ObjectId')


all_dates = sorted(set(df_germany.index.get_level_values(1)))
alle_langkreise = sorted(set(df_germany.index.get_level_values(0)))
earliest_date, last_date = all_dates[0], all_dates[-1]

landkreis_options = [{'label': df_germany.loc[lk, :].iloc[0, :]["Landkreis"] + f' ({lk})', 'value': lk} for lk in
                     alle_langkreise]


def reformat_line_y(start_date, end_date, locs, col_name):
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    y: pd.Series = df_germany.loc[locs, :][col_name].drop_duplicates()
    y.loc[start_date] = 0
    y.loc[end_date] = y[-2]
    y = y.sort_index()
    y = y.resample('D').ffill().values
    return y


def reformat_box_y(start_date, end_date, locs, col_name, indicator_col):
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    y: pd.Series = df_germany[df_germany[indicator_col].isin([0, 1])].loc[pd.IndexSlice[locs, :], [col_name]].groupby(
        ['Meldedatum']).sum().iloc[:, 0]
    y.loc[start_date] = 0
    y.loc[end_date] = y[-2]
    y = y.sort_index()
    y = y.resample('D').first().fillna(0).values
    return y


def get_germany_intital_layout():
    return html.Div([

        html.H1("Fallzahlen Deutschland nach Landkreisen", style={'text-align': 'center', 'font-family': 'Arial'}),
        html.Div([
            html.Div(
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=earliest_date,
                    max_date_allowed=last_date,
                    initial_visible_month=last_date,
                    end_date=last_date,
                    start_date=earliest_date,
                    display_format='DD.MM.YYYY',
                ),
                style={'width': '50%'}
            ),
            html.Div(
                dcc.Dropdown(
                    id='loc-dropdown',
                    options=landkreis_options,
                    value=5774,
                    multi=False,
                ),
                style={'width': '50%'}
            )], 'menu_container', style={'display': 'flex', 'align-items': 'center', 'font-family': 'Arial'}),
        html.Div(
            dcc.Graph(
                id='ger-line-graph',
                figure={
                    'data': [
                        {'x': all_dates, 'y': df_germany.loc[pd.IndexSlice[1001, :], "Kumulative Fälle"],
                         'range_x': [str(earliest_date), str(last_date)], 'type': 'line',
                         'name': 'new cases'}
                    ],
                    'layout': {
                        'title': 'Kumulative Fälle'}
                }
            ),
        ),
        html.Div(
            dcc.Graph(
                id='ger-bar-graph',
                figure={
                    'data': [
                        {'x': all_dates, 'y': df_germany.loc[pd.IndexSlice[1001, :], "AnzahlFall"],
                         'range_x': [str(earliest_date), str(last_date)], 'type': 'bar',
                         'name': 'Neue Fälle'},
                        {'x': all_dates, 'y': df_germany.loc[pd.IndexSlice[1001, :], "AnzahlGenesen"],
                         'range_x': [str(earliest_date), str(last_date)], 'type': 'bar',
                         'name': 'Anzahl genesen'},
                        {'x': all_dates, 'y': df_germany.loc[pd.IndexSlice[1001, :], "AnzahlTodesfall"],
                         'range_x': [str(earliest_date), str(last_date)], 'type': 'bar',
                         'name': 'Anzahl der Todesfälle'}
                    ],

                    'layout': {
                        'title': 'Tägliche Veränderung',

                    }
                }
            ),
        ),
        html.Div(
            dcc.Dropdown(
                id='cause-dropdown',
                options=[
                    {'label': 'Registrierte Fälle', 'value': 'AnzahlFall,NeuerFall,Registrierte Fälle'},
                    {'label': 'Genese Fälle', 'value': 'AnzahlGenesen,NeuGenesen,Genesene Personen'},
                    {'label': 'Todesfälle', 'value': 'AnzahlTodesfall,NeuerTodesfall,Todesfälle'},
                ],
                value='AnzahlFall,NeuerFall,Registrierte Fälle',
                multi=False,
            ),
            style={'width': '50%', 'font-family': 'Arial'}
        ),
        html.Div([
            html.Div([
                dcc.Graph(id='pie_age')
            ], style={'width': '50%'}),
            html.Div([
                dcc.Graph(id='pie_gender')
            ], style={'width': '50%'}),
        ], style={'display': 'flex'}),

    ])


@app.callback(
    [Output(component_id='ger-line-graph', component_property='figure'),
     Output(component_id='ger-bar-graph', component_property='figure'),
     Output(component_id='pie_age', component_property='figure'),
     Output(component_id='pie_gender', component_property='figure')],
    [Input(component_id='my-date-picker-range', component_property='start_date'),
     Input(component_id='my-date-picker-range', component_property='end_date'),
     Input(component_id='loc-dropdown', component_property='value'),
     Input(component_id='cause-dropdown', component_property='value')]
)
def germany_update_graph(start_date, end_date, locs, cause):
    current_kreis = df_germany.loc[locs, :].iloc[0, :]["Landkreis"]
    if locs is None:
        locs = 5766
    if start_date is None:
        start_date = earliest_date

    cause_col, cause_indiator, title = cause.split(',')
    general_loc = df_germany.loc[pd.IndexSlice[5774, :], :]
    age = general_loc[general_loc[cause_indiator].isin([0, 1])].groupby(['Altersgruppe']).sum()[cause_col]
    possible_keys_age = ['A00-A04', 'A05-A14', 'A15-A34', 'A35-A59', 'A60-A79', 'A80+']
    age_new = ['👶🏼 0-4', '👧🏼 5-14', '👱🏻‍♀ 15-34', '👨🏻 35-59', '👴🏻 60-79', '👵🏻 80+']
    age_mapping = dict(zip(possible_keys_age, age_new))
    age.index = [age_mapping[key] for key in age.index]

    gender = general_loc[general_loc[cause_indiator].isin([0, 1])].groupby(['Geschlecht']).sum()[cause_col]
    possible_genders = ['M', 'W', 'unbekannt']
    gender_new = ['👱🏻‍♂️ M', '👸🏼 W', 'unbekannt']
    gender_mapping = dict(zip(possible_genders, gender_new))
    gender.index = [gender_mapping[key] for key in gender.index]

    x = pd.Series(index=[pd.to_datetime(start_date), pd.to_datetime(end_date)]).resample('D').ffill().index.values
    x = [ts(y).strftime('%Y-%m-%d') for y in x]

    line_figure = {
        'data': [
            {'x': x, 'y': reformat_line_y(start_date, end_date, locs, "Kumulative Fälle"),
             'range_x': [x[0], x[-1]], 'type': 'line',
             'name': '🤒 Kumulative Fälle'},
            {'x': x, 'y': reformat_line_y(start_date, end_date, locs, "Kumulative Genesene"),
             'range_x': [x[0], x[-1]], 'type': 'line',
             'name': '🤗 Kumulative Genesene'},
            {'x': x, 'y': reformat_line_y(start_date, end_date, locs, "Kumulative Todefälle"),
             'range_x': [x[0], x[-1]], 'type': 'line',
             'name': '💀 Kumulative Todefälle'}
        ],
        'layout': {
            'title': f'📈 Kumulative Fälle in {current_kreis}'}
    }
    bar_figure = {
        'data': [

            {'x': x, 'y': reformat_box_y(start_date, end_date, locs, 'AnzahlFall', 'NeuerFall'),
             'range_x': [x[0], x[-1]], 'type': 'bar',
             'name': '🤒 Neue Fälle'},

            {'x': x, 'y': reformat_box_y(start_date, end_date, locs, 'AnzahlGenesen', 'NeuGenesen'),
             'range_x': [x[0], x[-1]], 'type': 'bar',
             'name': '🤗 Anzahl genesen'},
            {'x': x, 'y': reformat_box_y(start_date, end_date, locs, 'AnzahlTodesfall', 'NeuerTodesfall'),
             'range_x': [x[0], x[-1]], 'type': 'bar',
             'name': '💀 Anzahl der Todesfälle'}
        ],
        'layout': {
            'title': f'📆 Tägeliche Veränderungen in {current_kreis}'},
    }

    pie_age = px.pie(
        data_frame=age,
        names=age.index,
        values=age,
        hole=.3,
        title=f'👶🏼 / 👵🏻 {title} nach Altersgruppe in {current_kreis}'
    )
    pie_gender = px.pie(
        data_frame=gender,
        names=gender.index,
        values=gender,
        title=f'👸🏼 / 🤴🏻 {title} nach Geschlecht in {current_kreis}',
        hole=.3,
    )
    return line_figure, bar_figure, pie_age, pie_gender


#### END GERMANY #####

# -- data -- #

# URL of geojson
geojson_url = 'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson'
# with open('./data/countries.geojson') as response:
# with urlopen(geojson_url) as response:
with urllib.request.urlopen(geojson_url) as response:
    countries = json.load(response)

world_url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"

# -- dataframe for stuff from world_graphs -- #
df_world = pd.read_csv(world_url)
df_world['date'] = pd.to_datetime(df_world['date'])
daterange = pd.date_range(start=df_world['date'].min(), end=df_world['date'].max())

features = [df_world[column] for column in df_world]

# -- end: dataframe for stuff from world_graphs -- #

# -- TODO is df necessary? df: dataframe originally in app.py -- #
df = pd.read_csv(world_url)
df = df[df.location != "World"]
# print(list(df.columns))

logo_filename = './data/logo_upb.png'
encoded_image = base64.b64encode(open(logo_filename, 'rb').read())


# -- data end -- #

# -- functions for (re)converting time data for slider -- #

# the functions unixTimeMillis, unixToDatetime and getMarks are taken from Nils' post on
# https://stackoverflow.com/questions/51063191/date-slider-with-plotly-dash-does-not-work
# and were slightly adapted
def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))


def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    # off by 2 hours for dates after 29.3.2020 (i.e., calculates day prior, 22h),
    # before that, off by 1 hour
    off = pd.to_datetime(unix, unit='s')
    date_clock_change1 = pd.to_datetime('2020-03-29')
    date_clock_change2 = pd.to_datetime('2020-10-25')
    # TODO using these conditions, app will only work until 27.3.2021 (next change to summer time)
    if off >= date_clock_change1 and off < date_clock_change2:
        date = off + pd.to_timedelta(2, unit='h')
    else:
        date = off + pd.to_timedelta(1, unit='h')
    return date


def getMarks(start, end, Nth):
    ''' Returns the marks for labeling.
        Every Nth value will be used.
    '''

    result = {}
    for i, date in enumerate(daterange):
        if (i % Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result


# -- end: functions for (re)converting time data for slider -- #

# -- functions for creating world graphs -- #

def div_cases_deaths():
    return html.Div(dcc.Graph(id='graph-with-slider-cases-deaths'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


def div_cases_deaths_per_million():
    return html.Div(dcc.Graph(id='graph-with-slider-cases-deaths-per-million'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


def div_facilities():
    return html.Div(dcc.Graph(id='graph-with-slider-facilities-deaths'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


# -- end: functions for creating world graphs -- #

# -- functions for creating control elements for world graphs -- #

# alternative for choosing the date for which the data is shown, use in combination with update_output(date)
# def div_date_picker():
#     return html.Div([
#         (dcc.DatePickerSingle(
#             id = 'date-picker-single',
#             min_date_allowed = df_world.date.min(), # dt(1995, 8, 5),
#             max_date_allowed = df_world.date.max(), # dt(2017, 9, 19),
#             initial_visible_month = df_world.date.max(), # dt(2017, 8, 5),
#             date = df_world.date.min())
#         ),
#         html.Div(id='output-container-date-picker-single')])

def div_radio_axis_type(id, default, label):
    """

    :type id: str
    :type default: must be 'Linear' or 'Log'
    """
    return html.Div([
        html.Label(label),
        dcc.RadioItems(
            id=id,
            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            value=default,
            labelStyle={'display': 'inline-block'}
        )], style={'float': 'left', 'padding': '20px 20px 20px 20px'})


# todo
def div_panel(div):
    """

    :type div: list of 2 elements that should be shown together (e.g. selection for type of x- and y-axis)
    """
    return html.Div([
        div[0],
        div[1]
    ]  # , style={'display': 'inline-block'}
    )


def div_slider():
    # dcc.Sliders don't work with timestamps/dates, only with numeric values
    return html.Div(dcc.Slider(

        id='date-slider',
        min=unixTimeMillis(daterange.min()),
        max=unixTimeMillis(daterange.max()),
        value=unixTimeMillis(daterange.max()),
        # marks=getMarks(daterange.min(),
        #                daterange.max(),7),
        step=None,  # only dates selectable for which there is a mark entry
        marks=getMarks(daterange.min(),
                       daterange.max(), 14),
        # data is available only 1x per day; restrict user to these steps
        # else, no data being shown because no data exists e.g. for 2020-03-29 14:07:00
        # step=unixTimeMillis(pd.to_timedelta(1, unit='d')), #TODO doesn't work because timedelta has no timetuple attribute
        vertical=True
    ), style={'width': '20%', 'padding': '0px 20px 20px 20px', 'float': 'right', 'display': 'inline-block'})


# -- end: functions for creating control elements for world graphs -- #

# -- end: data -- #

# -- functions for (re)converting time data for slider -- #

# the functions unixTimeMillis, unixToDatetime and getMarks are taken from Nils' post on
# https://stackoverflow.com/questions/51063191/date-slider-with-plotly-dash-does-not-work
# and were slightly adapted
def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))


def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    # off by 2 hours for dates after 29.3.2020 (i.e., calculates day prior, 22h),
    # before that, off by 1 hour
    off = pd.to_datetime(unix, unit='s')
    date_clock_change1 = pd.to_datetime('2020-03-29')
    date_clock_change2 = pd.to_datetime('2020-10-25')
    # TODO using these conditions, app will only work until 27.3.2021 (next change to summer time)
    if off >= date_clock_change1 and off < date_clock_change2:
        date = off + pd.to_timedelta(2, unit='h')
    else:
        date = off + pd.to_timedelta(1, unit='h')
    return date


def getMarks(start, end, Nth):
    ''' Returns the marks for labeling.
        Every Nth value will be used.
    '''

    result = {}
    for i, date in enumerate(daterange):
        if (i % Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result


# -- end: functions for (re)converting time data for slider -- #

# -- functions for creating world graphs -- #

def div_cases_deaths():
    return html.Div(dcc.Graph(id='graph-with-slider-cases-deaths'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


def div_cases_deaths_per_million():
    return html.Div(dcc.Graph(id='graph-with-slider-cases-deaths-per-million'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


def div_facilities():
    return html.Div(dcc.Graph(id='graph-with-slider-facilities-deaths'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


# -- end: functions for creating world graphs -- #

# -- functions for creating control elements for world graphs -- #

# alternative for choosing the date for which the data is shown, use in combination with update_output(date)
# def div_date_picker():
#     return html.Div([
#         (dcc.DatePickerSingle(
#             id = 'date-picker-single',
#             min_date_allowed = df_world.date.min(), # dt(1995, 8, 5),
#             max_date_allowed = df_world.date.max(), # dt(2017, 9, 19),
#             initial_visible_month = df_world.date.max(), # dt(2017, 8, 5),
#             date = df_world.date.min())
#         ),
#         html.Div(id='output-container-date-picker-single')])

def div_radio_axis_type(id, default, label):
    """

    :type id: str
    :type default: must be 'Linear' or 'Log'
    """
    return html.Div([
        html.Label(label),
        dcc.RadioItems(
            id=id,
            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
            value=default,
            labelStyle={'display': 'inline-block'}
        )], style={'float': 'left', 'padding': '20px 20px 20px 20px'})


# todo
def div_panel(div):
    """

    :type div: list of 2 elements that should be shown together (e.g. selection for type of x- and y-axis)
    """
    return html.Div([
        div[0],
        div[1]
    ]  # , style={'display': 'inline-block'}
    )


def div_slider():
    # dcc.Sliders don't work with timestamps/dates, only with numeric values
    return html.Div(dcc.Slider(

        id='date-slider',
        min=unixTimeMillis(daterange.min()),
        max=unixTimeMillis(daterange.max()),
        value=unixTimeMillis(daterange.max()),
        # marks=getMarks(daterange.min(),
        #                daterange.max(),7),
        step=None,  # only dates selectable for which there is a mark entry
        marks=getMarks(daterange.min(),
                       daterange.max(), 14),
        # data is available only 1x per day; restrict user to these steps
        # else, no data being shown because no data exists e.g. for 2020-03-29 14:07:00
        # step=unixTimeMillis(pd.to_timedelta(1, unit='d')), #TODO doesn't work because timedelta has no timetuple attribute
        vertical=True
    ), style={'width': '20%', 'padding': '0px 20px 20px 20px', 'float': 'right', 'display': 'inline-block'})


# -- end: functions for creating control elements for world graphs -- #

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

df_location = df.copy()
df_location = df_location['location']
locations = list(np.unique(df_location))
dff = df.copy()
dff = dff[dff['location'] == 'World']
group = ['All']
group = group + ['Low', 'Medium', 'High', 'Very High']
graph_options = ['total_cases vs. total_deaths',
                 'total_cases_per_million vs. total_deaths_per_million',
                 'handwashing_facilities vs. total_cases_per_million']
group_class = [{'label': str(item),
                'value': str(item)}
               for item in graph_options]  # in group]

graph_options_dict = [{
    # TODO along group_class
    ''
}]

# components style
# ------------ #

fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'], font_color=colors['text'])

# logo_filename = 'logo_upb.png'
logo_filename = 'data/logo_upb.png'
encoded_image = base64.b64encode(open(logo_filename, 'rb').read())

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
                    dcc.RadioItems(
                        id='Dataset',
                        options=[
                            {'label': 'World', 'value': 'World'},
                            {'label': 'Germany', 'value': 'Germany'},
                        ],
                        value='World',
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
                        options=group_class,
                        multi=False,
                        value='Select'
                    )
                ],
                className='two columns',
                style={'margin-top': '10'}
            ),
            html.Div(
                [
                    html.P('Select a graph to be displayed:'),
                    dcc.Dropdown(
                        id='graph_selection_1',
                        options=group_class,
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
                ], className="six columns"
            ),
            html.Div(
                [
                    # bar chart
                    dcc.Graph(id='bar-graph',
                              figure={
                                  'data': [
                                      {'x': dff['date'], 'y': dff['new_cases'], 'range_x': ['2020-02-02', '2020-07-31'],
                                       'type': 'bar', 'name': 'new cases'},
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
                                      {'x': dff['date'], 'y': dff['total_cases'],
                                       'range_x': ['2020-02-02', '2020-07-31'], 'type': 'line', 'name': 'total cases'}
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
    ),
    # inserted from world_graphs.py
    # div_date_picker(), # use a calendar to choose date for which data is to be shown (instead of slider)
    div_panel([
        div_radio_axis_type('x_cases_death', 'Log', 'horizontal axis:'),
        div_radio_axis_type('y_cases_death', 'Log', 'vertical axis:')
    ]),
    div_cases_deaths(),

    div_slider(),

    div_panel([
        div_radio_axis_type('x_death_per_million', 'Linear', 'horizontal axis:'),
        div_radio_axis_type('y_death_per_million', 'Linear', 'vertical axis:')
    ]),
    div_cases_deaths_per_million(),

    div_panel([
        div_radio_axis_type('x_facilities', 'Linear', 'horizontal axis:'),
        div_radio_axis_type('y_facilities', 'Linear', 'vertical axis:')
    ]),
    div_facilities(),
    get_germany_intital_layout()
], className='ten columns offset-by-one')


# -- end of components -- #

# ---------- #

# -- callbacks and functions -- #

# TODO callback 
# @app.callback(
#     Output('graph_1', 'figure'),
#     # [Input('xaxis-column', 'value'),
#     #  Input('yaxis-column', 'value'),
#     #  Input('xaxis-type', 'value'),
#     #  Input('yaxis-type', 'value'),
#     #  Input('year--slider', 'value')]
#     [Input('graph-id', 'value')]
# )
# def update_graph(graph_option):
#     fig = ...
#     return fig

@app.callback(
    dash.dependencies.Output('loc_dropdown', 'options'),
    [dash.dependencies.Input('Dataset', 'value')])
def set_location_options(selected_dataset):
    if selected_dataset == 'World':
        return [{'label': i, 'value': i} for i in locations]
    if selected_dataset == 'Germany':
        return [{'label': i, 'value': i} for i in german_locations]


@app.callback(
    dash.dependencies.Output('loc_dropdown', 'value'),
    [dash.dependencies.Input('loc_dropdown', 'options')])
def set_location_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('graph-with-slider-cases-deaths', 'figure'),
    [Input('date-slider', 'value'),
     Input('x_cases_death', 'value'),
     Input('y_cases_death', 'value')])
def update_figure(selected_date, xaxis_type, yaxis_type):
    filtered_df = df_world[(df_world.date == unixToDatetime(selected_date))
                           & (df_world.location != 'World')
                           & (df_world.location != 'International')]
    filtered_df = filtered_df.fillna('unspecified')

    fig = px.scatter(filtered_df,
                     x='total_cases',
                     y='total_deaths',
                     color=filtered_df.continent,
                     hover_name=filtered_df.location,
                     hover_data=['population'])

    fig.update_xaxes(type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(type='linear' if yaxis_type == 'Linear' else 'log')
    fig.update_layout(transition_duration=500)

    return fig


@app.callback(
    Output('graph-with-slider-cases-deaths-per-million', 'figure'),
    [Input('date-slider', 'value'),  # alternatively: Input('date-picker-single', 'date'),
     Input('x_death_per_million', 'value'),
     Input('y_death_per_million', 'value')])
def update_figure_per_million(selected_date, xaxis_type, yaxis_type):
    # when using date-picker-single, just use selected_date without transformation for filtering
    filtered_df = df_world[(df_world.date == unixToDatetime(selected_date))
                           & (df_world.location != 'World')
                           & (df_world.location != 'International')]
    filtered_df = filtered_df.fillna('unspecified')

    fig = px.scatter(filtered_df,
                     x='total_cases_per_million',
                     y='total_deaths_per_million',
                     color=filtered_df.continent,
                     # animation_frame='date',
                     hover_name=filtered_df.location,
                     hover_data=['population', 'hospital_beds_per_thousand', 'extreme_poverty']
                     )

    fig.update_xaxes(type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(type='linear' if yaxis_type == 'Linear' else 'log')
    fig.update_layout(transition_duration=500)

    return fig


@app.callback(
    Output('graph-with-slider-facilities-deaths', 'figure'),
    [Input('date-slider', 'value'),
     Input('x_facilities', 'value'),
     Input('y_facilities', 'value')])
def update_figure_facilities(selected_date, xaxis_type, yaxis_type):
    filtered_df = df_world[(df_world.date == unixToDatetime(selected_date))
                           & (df_world.location != 'World')
                           & (df_world.location != 'International')]
    filtered_df = filtered_df.fillna('unspecified')

    fig = px.scatter(filtered_df,
                     x='handwashing_facilities',
                     y='total_cases_per_million',
                     color=filtered_df.continent,
                     hover_name=filtered_df.location,
                     hover_data=['hospital_beds_per_thousand', 'total_deaths', 'population']
                     )

    fig.update_xaxes(title='percentage of population with basic handwashing facilities',
                     type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(type='linear' if yaxis_type == 'Linear' else 'log')
    fig.update_layout(transition_duration=500)

    return fig


# alternative for choosing the date for which the data is shown, use in combination with date-picker-single
# @app.callback(
#     Output('output-container-date-picker-single', 'children'),
#     [Input('date-picker-single', 'date')])
# def update_output(date):
#     string_prefix = 'Data is shown for: '
#     if date is not None:
#         date = datetime.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
#         date_string = date.strftime('%B %d, %Y')
#         return string_prefix + date_string

# -- end: callbacks and functions -- #

# ---------- # 

if __name__ == '__main__':
    app.run_server(debug=True)
