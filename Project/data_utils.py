from os.path import join as pjoin
import pandas as pd
import pycountry

continents = [
    'North America',
    'Latin America & Caribbean',
    'South Africa',
    'Middle East & North Africa',
    'Europe & Central Asia',
    # 'Central Europe and the Baltics',
    'East Asia & Pacific',
    'South Asia',
    'Australia',
]

def get_df(subdir, fname, continent=False):
    df = pd.read_csv(pjoin('data', subdir, fname), header=2).iloc[:,:-3].dropna()
    if continent:
        df_continent = df.set_index(df['Country Name']).loc[:,'1960':]
        df_continent = df_continent.loc[map(lambda x: x in continents, df_continent.index)]
        df_continent.columns = df_continent.columns.astype(int)
    df = df.set_index(df['Country Code']).loc[:,'1960':]
    df = df.loc[map(lambda x: pycountry.countries.get(alpha_3=x) is not None, df.index)]
    df.columns = df.columns.astype(int)
    print(df.shape)
    if continent:
        return df, df_continent
    return df

def get_all_countries(dfs):
    all_countries = sorted(list(set.intersection(*[set(dfs[key].index) for key in dfs])))
    print(len(all_countries), "countries")
    return all_countries

def unify_dfs(dfs, countries):
    for key in dfs:
        dfs[key] = dfs[key].loc[countries]
    return dfs

def get_data():
    df_f, df_f_c = get_df('fertility-rate', 'API_SP.DYN.TFRT.IN_DS2_en_csv_v2_10474146.csv', True)
    df_le, df_le_c = get_df('life-expectancy-at-birth', 'API_SP.DYN.LE00.IN_DS2_en_csv_v2_10473758.csv', True)
    df_pop, df_pop_c = get_df('population', 'API_SP.POP.TOTL_DS2_en_csv_v2_10473719.csv', True)
    df_br, df_br_c = get_df('birth-rate-crude', 'API_SP.DYN.CBRT.IN_DS2_en_csv_v2_10475710.csv', True)
    df_dr, df_dr_c = get_df('death-rate-crude', 'API_SP.DYN.CDRT.IN_DS2_en_csv_v2_10474583.csv', True)
    dfs = {
        'fertility': df_f,
        'life': df_le,
        'population': df_pop,
        'birth': df_br,
        'death': df_dr
    }
    dfs_continents = {
        'fertility': df_f_c,
        'life': df_le_c,
        'population': df_pop_c,
        'birth': df_br_c,
        'death': df_dr_c
    }
    codes = get_all_countries(dfs)
    dfs = unify_dfs(dfs, codes)
    names = []
    for iso3code in codes:
        country = pycountry.countries.get(alpha_3=iso3code)
        names.append(country.name)
    return dfs, dfs_continents, codes, names

if __name__ == "__main__":
    dfs, dfs_continents, codes, names = get_data()