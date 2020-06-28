from datetime import datetime

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
ts = lambda dt64: datetime.utcfromtimestamp((dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))

df = pd.read_pickle('./../data/data_germany.pickle').drop_duplicates('ObjectId')

all_dates = sorted(set(df.index.get_level_values(1)))
alle_langkreise = sorted(set(df.index.get_level_values(0)))
earliest_date, last_date = all_dates[0], all_dates[-1]

print(f"Frühster Tag: {earliest_date} {type(earliest_date)}\nSpätester Tag: {last_date}")

landkreis_options = [{'label': df.loc[lk, :].iloc[0, :]["Landkreis"] + f' ({lk})', 'value': lk} for lk in
                     alle_langkreise]
print(len(landkreis_options))

app.layout = html.Div([

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
            id='line-graph',
            figure={
                'data': [
                    {'x': all_dates, 'y': df.loc[pd.IndexSlice[1001, :], "Kumulative Fälle"],
                     'range_x': [str(earliest_date), str(last_date)], 'type': 'line',
                     'name': 'new cases'}
                ],
                'layout': {
                    'title': 'Kumulative Fälle'}
            }
        ),
        # style={'float': 'left', 'position': 'relative', 'width': '50%'}
    ),
    html.Div(
        dcc.Graph(
            id='bar-graph',
            figure={
                'data': [
                    {'x': all_dates, 'y': df.loc[pd.IndexSlice[1001, :], "AnzahlFall"],
                     'range_x': [str(earliest_date), str(last_date)], 'type': 'bar',
                     'name': 'Neue Fälle'},
                    {'x': all_dates, 'y': df.loc[pd.IndexSlice[1001, :], "AnzahlGenesen"],
                     'range_x': [str(earliest_date), str(last_date)], 'type': 'bar',
                     'name': 'Anzahl genesen'},
                    {'x': all_dates, 'y': df.loc[pd.IndexSlice[1001, :], "AnzahlTodesfall"],
                     'range_x': [str(earliest_date), str(last_date)], 'type': 'bar',
                     'name': 'Anzahl der Todesfälle'}
                ],

                'layout': {
                    'title': 'Tägliche veränderung',

                }
            }
        ),
    )

])


def reformat_line_y(start_date, end_date, locs, col_name):
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    y: pd.Series = df.loc[locs, :][col_name].drop_duplicates()
    y.loc[start_date] = 0
    y.loc[end_date] = y[-2]
    y = y.sort_index()
    y = y.resample('D').ffill().values
    return y


def reformat_box_y(start_date, end_date, locs, col_name, indicator_col):
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    y: pd.Series = df[df[indicator_col].isin([0, 1])].loc[pd.IndexSlice[locs, :], [col_name]].groupby(
        ['Meldedatum']).sum().iloc[:, 0]
    y.loc[start_date] = 0
    y.loc[end_date] = y[-2]
    y = y.sort_index()
    y = y.resample('D').first().fillna(0).values
    return y


@app.callback(
    [Output(component_id='line-graph', component_property='figure'),
     Output(component_id='bar-graph', component_property='figure')],
    [Input(component_id='my-date-picker-range', component_property='start_date'),
     Input(component_id='my-date-picker-range', component_property='end_date'),
     Input(component_id='loc-dropdown', component_property='value')]
)
def update_graph(start_date, end_date, locs):
    print(locs, type(locs))
    current_kreis = df.loc[locs, :].iloc[0, :]["Landkreis"]
    if locs is None:
        locs = 5766
    if start_date is None:
        start_date = earliest_date

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
    return line_figure, bar_figure


if __name__ == '__main__':
    app.run_server(debug=True)
