# insert into section callbacks:

@app.callback(
    Output('graph_1', 'figure'),
    [Input('xaxis-column', 'value'), # value to be displayed on x-axis
     Input('yaxis-column', 'value'), # value to be displayed on y-axis
     Input('xaxis-type', 'value'), # log/lin
     Input('yaxis-type', 'value'), # log/lin
     Input('date-slider', 'value')] # date to be displayed
)
def update_graph_1(x_axis_column, y_axis_column,
                   x_axis_type, y_axis_type,
                   selected_date):
    filtered_df = df_world[(df_world.date == unixToDatetime(selected_date))
                           & (df_world.location != 'World')
                           & (df_world.location != 'International')]
    filtered_df = filtered_df.fillna('unspecified')

    fig = px.scatter(filtered_df,
                     x=x_axis_column,
                     y=y_axis_column,
                     color=filtered_df.continent,
                     hover_name=filtered_df.location,
                     hover_data=['population', 'hospital_beds_per_thousand', 'extreme_poverty'],
                     title='Worldwide data for selected date (' + unixToDatetime(selected_date).strftime('%Y-%m-%d') + ')')

    x_title = x_axis_column
    y_title = y_axis_column

    if x_axis_column == 'handwashing_facilities':
        x_title = 'percentage of population with basic handwashing facilities'
    elif x_axis_column == 'stringency_index':
        x_title = 'severity of restrictions from 0 to 100 (100 = strictest)'

    if y_axis_column == 'handwashing_facilities':
        y_title = 'percentage of population with basic handwashing facilities'
    elif y_axis_column == 'stringency_index':
        y_title = 'severity of restrictions from 0 to 100 (100 = strictest)'

    fig.update_xaxes(title=x_title, type='linear' if x_axis_type == 'Linear' else 'log')
    fig.update_yaxes(title=y_title, type='linear' if y_axis_type == 'Linear' else 'log')
    fig.update_layout(transition_duration=500)

    return fig

# insert into app.layout:

    div_radio_axis_type('xaxis-type', 'Linear', 'horizontal axis:'), # - RadioBox lin/log with id='xaxis-type', name ('horizontal...') can be anything
    div_radio_axis_type('yaxis-type', 'Linear', 'vertical axis:'),   # - RadioBox lin/log with id='yaxis-type'
    # - dropdown menu with id='xaxis-column'
    # - dropdown menu with id='yaxis-column'
    html.Div(
        [
            html.P('Select x axis:'),
            dcc.Dropdown(
                id='xaxis-column',
                options= column_class,
                multi=False,
                value='total_cases'
            )
        ]),
    html.Div(
        [
            html.P('Select y axis:'),
            dcc.Dropdown(
                id='yaxis-column',
                options= column_class,
                multi=False,
                value='total_deaths'
            )
        ]),
    dcc.Graph(id='graph_1') # for displaying 1 of my possible graphs


# insert in section dropdown, button (before app.layout):

column_options = ['total_cases', 'total_deaths',
                  'total_cases_per_million', 'total_deaths_per_million',
                  'new_cases', 'new_cases_per_million',
                  'handwashing_facilities', 'stringency_index',
                  'population_density']
column_class = [{'label': str(item),
                 'value': str(item)}
                for item in column_options]
