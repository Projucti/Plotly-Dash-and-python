import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output

# Author: Taslima Akter


# -----------Reading data from world data-------------
external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = pd.read_csv('wdata.csv')
# ------------dropdown dynamic for selecting country--------------
df_location = df.copy()
df_location = df_location['location']
locations = list(np.unique(df_location))
dff = df.copy()
dff = dff[dff['location'] == 'World']
# ------------Visualizing data for World as default-------------
app.layout = html.Div([
    html.H1('COVID-19 CORONAVIRUS PANDEMIC'),

    html.Div('''
        A visulization in Bar and line graph
    '''),
    dcc.Dropdown(id='loc_dropdown',
                 options=[
                     {'label': location, 'value': location} for location in locations
                 ],
                 multi=False,
                 value='World',
                 style={'width': '40%'}
                 ),
    html.Div(id="output_container", children=[]),
    html.Br(),
    html.Div(
        dcc.Graph(
            id='bar-graph',
            figure={
                'data': [
                    {'x': dff['date'], 'y': dff['new_cases'], 'range_x': ['2020-02-02', '2020-07-31'], 'type': 'bar',
                     'name': 'new cases'}
                ],
                'layout': {
                    'title': 'Daily new cases for World'}
            }
        ),
        style={'float': 'left', 'position': 'relative', 'width': '50%'}),
    html.Div(
        dcc.Graph(
            id='line-graph',
            figure={
                'data': [
                    {'x': dff['date'], 'y': dff['total_cases'], 'range_x': ['2020-02-02', '2020-07-31'], 'type': 'line',
                     'name': 'total cases'}
                ],
                'layout': {
                    'title': 'Total Coronavirus cases for World'}
            }
        ),
        style={'float': 'right', 'position': 'relative', 'width': '50%'})
])


# ------------updating graph as per user selection---------------------
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='bar-graph', component_property='figure'),
     Output(component_id='line-graph', component_property='figure')],
    [Input(component_id='loc_dropdown', component_property='value')]
)
def update_graph(selected_option):
    print(selected_option)
    print(type(selected_option))

    container = "The selected location by user is: {}".format(selected_option)

    dff_new = df.copy()
    dff_new = dff_new[dff_new['location'] == selected_option]
    print(dff)
    figure = {
        'data': [
            {'x': dff_new['date'], 'y': abs(dff_new['new_cases']), 'range_x': ['2020-02-02', '2020-07-31'],
             'type': 'bar', 'name': 'cases'}
        ],
        'layout': {
            'title': 'Daily new cases for {}'.format(selected_option)}
    }
    line_figure = {
        'data': [
            {'x': dff_new['date'], 'y': abs(dff_new['total_cases']), 'range_x': ['2020-02-02', '2020-07-31'],
             'type': 'line', 'name': 'total cases'}
        ],
        'layout': {
            'title': 'Total Coronavirus cases for {}'.format(selected_option)}
    }

    return container, figure, line_figure


if __name__ == '__main__':
    app.run_server(debug=True)
