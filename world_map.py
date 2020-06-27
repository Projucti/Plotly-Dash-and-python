import json
from urllib.request import urlopen
import pandas as pd
import plotly.express as px

# URL of geojson
# with urlopen('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson') as response:
with open('./data/countries.geojson') as response:
    countries = json.load(response)

df = pd.read_csv('./data/wdata.csv')
df = df[df.location != "World"]
print(list(df.columns))

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
fig.show()
