import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import time


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

world_url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
df_world = pd.read_csv(world_url)
df_world['date'] = pd.to_datetime(df_world['date'])
daterange = pd.date_range(start=df_world['date'].min(),end=df_world['date'].max())

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
    off = pd.to_datetime(unix,unit='s')
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
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%Y-%m-%d'))

    return result


def div_cases_deaths():
    return html.Div(dcc.Graph(id='graph-with-slider-cases-deaths'),
                    style={'width': '75%', 'padding': '0px 20px 20px 20px', 'float': 'left', 'display': 'inline-block'})

def div_slider():
    # dcc.Sliders don't work with timestamps/dates, only with numeric values
    return html.Div(dcc.Slider(

        id='date-slider',
        min = unixTimeMillis(daterange.min()),
        max = unixTimeMillis(daterange.max()),
        value = unixTimeMillis(daterange.max()),
        # marks=getMarks(daterange.min(),
        #                daterange.max(),7),
        step=None, # only dates selectable for which there is a mark entry
        marks=getMarks(daterange.min(),
                       daterange.max(),14),
        # data is available only 1x per day; restrict user to these steps
        # else, no data being shown because no data exists e.g. for 2020-03-29 14:07:00
        #step=unixTimeMillis(pd.to_timedelta(1, unit='d')), #TODO doesn't work because timedelta has no timetuple attribute
        vertical=True
    ), style={'width': '20%', 'padding': '0px 20px 20px 20px', 'float': 'right', 'display': 'inline-block'})


app.layout = html.Div([
    div_cases_deaths(),
    div_slider()

])


@app.callback(
    Output('graph-with-slider-cases-deaths', 'figure'),
    [Input('date-slider', 'value')])
def update_figure(selected_date):
    filtered_df = df_world[(df_world.date == unixToDatetime(selected_date)) & (df_world.location != 'World')]
    filtered_df = filtered_df.fillna('unspecified')

    fig = px.scatter(filtered_df,
                     x='total_cases',
                     y='total_deaths',
                     color=filtered_df.continent,
                     hover_name=filtered_df.location)

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
