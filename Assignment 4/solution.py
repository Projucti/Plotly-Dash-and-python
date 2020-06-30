import pandas as pd
import plotly.express as px
import seaborn as sns
from matplotlib import pyplot as plt


df = pd.read_csv("DataWeierstrass.csv", delimiter=";")

df_norm = df.copy()
df_norm.iloc[:, 3:] = df.iloc[:, 3:].mul(df["participants"], axis=0)
df_norm = df_norm.groupby("professor").sum().reset_index()
df_norm.iloc[:, 2:] = df_norm.iloc[:, 2:].div(df_norm["participants"], axis=0)

markers = ['o', '+', 'x', 's', 'p']
markers = (markers * (1 + int(df_norm.shape[0] / len(markers))))[:-(-df_norm.shape[0] % len(markers))]

plt.style.use("ggplot")
plt.title('Weierstrass')
g = sns.PairGrid(df_norm, hue="professor", hue_kws={"marker": markers})
g.map(plt.scatter)
g.add_legend()
plt.savefig("scatter.png", dpi=200)
plt.clf()

df_norm['professor'] = df_norm.reset_index()['index'] + 1
fig = px.parallel_coordinates(df_norm, color_continuous_scale=px.colors.qualitative.Light24, color="professor")
fig.update(layout_coloraxis_showscale=False)
fig.show()
