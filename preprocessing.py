import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
plt.style.use("ggplot")

def downlaod_data():
    rki_url = "https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.csv"
    df_rki = pd.read_csv(rki_url)
    df_rki['Meldedatum'] = pd.to_datetime(df_rki['Meldedatum'])
    df_rki.drop(["Refdatum", 'Datenstand', 'Altersgruppe2'], axis=1, inplace=True)
    df_rki = df_rki.sort_values(["IdLandkreis", 'Meldedatum']).set_index(["IdLandkreis", 'Meldedatum'])
    return df_rki


def reduce_berlin(df_rki):
    df_berlin = df_rki[df_rki['IdBundesland'] == 11].reset_index(level=0, drop=True)

    to_drop_berlin = list()
    for index_berlin_alt in set(df_rki[df_rki['IdBundesland'] == 11].index.get_level_values(0)):
        to_drop_berlin.append(index_berlin_alt)

    df_rki.drop(to_drop_berlin, axis=0, level=0, inplace=True)

    df_berlin.loc[:, "IdLandkreis"] = [11000] * (df_berlin.shape[0])
    df_berlin = df_berlin.reset_index().set_index(['IdLandkreis', "Meldedatum"])
    df_rki = pd.concat([df_rki, df_berlin], axis=0)
    return df_rki

def per_einwohner(df_rki, kreis_mapping, spalte, ziel_name):
    series_result_list = list()
    for landkreis in set(df_rki.index.get_level_values(0)):
        _temp = df_rki.loc[pd.IndexSlice[landkreis, :], spalte].div(
            kreis_mapping.loc[landkreis, 'Bevölkerung_insgesamt']).multiply(100_000)
        series_result_list.append(_temp.rename(ziel_name))
    series_result = series_result_list[0].append(series_result_list[1:])
    return df_rki.join(series_result)

def read_kreis_mapping():
    kreis_to_int = lambda x, d_type: [d_type(y.replace(" ", "")) for y in x]

    col_names = ["Schlüssel-nummer", "Regionale_Bezeichnung", "Kreis/Landkreis", "NUTS3", "Fläche_in_km2",
             'Bevölkerung_insgesamt', 'Bevölkerung_männlich', 'Bevölkerung_weiblich', 'Bevölkerung_je_km2']
    df_kreis_data = pd.read_csv('./data/kreise_mapping.csv', sep=';', names=col_names).set_index("Schlüssel-nummer")
    df_kreis_data.dropna(inplace=True)  # Einträge der Bundesländer löschen
    df_kreis_data = df_kreis_data.iloc[:, 4:].apply(kreis_to_int, args = [(int)])

    df_kreis_data = df_kreis_data.convert_dtypes()
    return df_kreis_data


def get_cumulative_cases(df_rki, column_to_sum_up, column_indicator, target_column_name):
    df_fälle_landkreise = df_rki[df_rki[column_indicator].isin([0, 1])] \
        .pivot_table(values=column_to_sum_up, index='Meldedatum', columns=['IdLandkreis'], fill_value=0, aggfunc="sum") \
        .astype(float).cumsum().astype(int)
    df_fälle_landkreise.loc[pd.to_datetime(datetime.now().strftime("%Y-%m-%d")), :] = df_fälle_landkreise.iloc[-1, :]
    df_fälle_landkreise = df_fälle_landkreise.resample('D', axis=0).ffill()
    df_fälle_landkreise_melt = pd.melt(df_fälle_landkreise.reset_index(), id_vars='Meldedatum',
                                       value_name=target_column_name).set_index(['IdLandkreis', 'Meldedatum'])
    return df_rki.join(df_fälle_landkreise_melt).fillna(0).convert_dtypes()

def preprocess_and_laod_germany_data():
    df_rki = reduce_berlin(downlaod_data())
    print(df_rki.shape)
    df_rki = get_cumulative_cases(df_rki, 'AnzahlFall', 'NeuerFall', 'Kumulative Fälle')
    df_rki = get_cumulative_cases(df_rki, 'AnzahlGenesen', 'NeuGenesen', 'Kumulative Genesene')
    df_rki = get_cumulative_cases(df_rki, 'AnzahlTodesfall', 'NeuerTodesfall', 'Kumulative Todefälle')
    kreis_mapping = read_kreis_mapping()
    df_rki = per_einwohner(df_rki, kreis_mapping, "Kumulative Fälle", "Fälle/100k_Einwohner")
    # df_rki = per_einwohner(df_rki, kreis_mapping, "Kumulative Genesene", "Genesene/100k_Einwohner")
    # df_rki = per_einwohner(df_rki, kreis_mapping, "Kumulative Todefälle", "Tote/100k_Einwohner")
    return df_rki

if __name__ == '__main__':
    print(preprocess_and_laod_germany_data())
