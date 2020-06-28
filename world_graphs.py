import time

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

world_url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
df_world = pd.read_csv(world_url)
df_world['date'] = pd.to_datetime(df_world['date'])
daterange = pd.date_range(start=df_world['date'].min(), end=df_world['date'].max())

features = [df_world[column] for column in df_world]


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


def div_cases_deaths():
    return html.Div(dcc.Graph(id='graph-with-slider-cases-deaths'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


def div_cases_deaths_per_million():
    return html.Div(dcc.Graph(id='graph-with-slider-cases-deaths-per-million'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


def div_facilities():
    return html.Div(dcc.Graph(id='graph-with-slider-facilities-deaths'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})


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


app.layout = html.Div([
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
    div_facilities()

])


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
    [Input('date-slider', 'value'),
     Input('x_death_per_million', 'value'),
     Input('y_death_per_million', 'value')])
def update_figure_per_million(selected_date, xaxis_type, yaxis_type):
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
                     hover_data=['total_deaths', 'population', 'hospital_beds_per_thousand', 'extreme_poverty']
                     )

    fig.update_xaxes(title='percentage of population with basic handwashing facilities',
                     type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(type='linear' if yaxis_type == 'Linear' else 'log')
    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
