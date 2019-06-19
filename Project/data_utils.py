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

not_countries = [
    'Arab World',
    'Central Europe and the Baltics',
#     'Channel Islands', #?
#     'Caribbean small states' #?
    'East Asia & Pacific',
    'East Asia & Pacific (excluding high income)',
    'Early-demographic dividend',
    'Europe & Central Asia',
    'Europe & Central Asia (excluding high income)',
    'European Union',
    'IBRD only',
    'IDA & IBRD total',
    'IDA total',
    'IDA blend',
    'IDA only',
    'IDA blend',
    'High income',
#     'Hong Kong SAR, China',#?
    'Fragile and conflict affected situations',
    'Heavily indebted poor countries (HIPC)',
    'Late-demographic dividend',
    'Latin America & Caribbean',
    'Latin America & Caribbean (excluding high income)',
    'Least developed countries: UN classification',
    'Low income',
    'Lower middle income',
    'Low & middle income',
#     'Macao SAR, China',#?
    'Middle East & North Africa',
    'Middle East & North Africa (excluding high income)',
    'OECD members',
    'Other small states',
    'Post-demographic dividend',
    'Pre-demographic dividend',
    'East Asia & Pacific (IDA & IBRD countries)',
    'Europe & Central Asia (IDA & IBRD countries)',
    'Latin America & the Caribbean (IDA & IBRD countries)',
    'Middle East & North Africa (IDA & IBRD countries)',
    'Middle income',
    'South Asia (IDA & IBRD)',
    'Sub-Saharan Africa',
    'Sub-Saharan Africa (IDA & IBRD countries)',
    'Sub-Saharan Africa (excluding high income)',
    'World',
]

countries_replacement = {
    'Bahamas, The': 'The Bahamas',
    'Congo, Dem. Rep.': 'Democratic Republic of the Congo',
    'Congo, Rep.': 'Republic of the Congo',
    'Egypt, Arab Rep.': 'Arab Republic of Egypt',
    'Hong Kong SAR, China': 'Hong Kong Special Administrative Region of the People\'s Republic of China',
    'Gambia, The': 'The Gambia',
    'Lao PDR': 'Lao',
    'Micronesia, Fed. Sts.': 'The Federated States of Micronesia',
    'Iran, Islamic Rep.': 'Islamic Republic of Iran',
    'Macao SAR, China': 'Macao Special Administrative Region of the People\'s Republic of China', #Macau or Macao
    'Macedonia, FYR': 'Republic of North Macedonia',
    'Korea, Rep.': 'Republic of Korea', #South Korea
    'Korea, Dem. People’s Rep.': \
        'Democratic People\'s Republic of Korea', #North Korea
    'St. Lucia': 'Saint Lucia',
    'St. Vincent and the Grenadines':'Saint Vincent and the Grenadines',
    'Venezuela, RB': 'Bolivarian Republic of Venezuela',
    'Virgin Islands (U.S.)': 'United States Virgin Islands',
    'Yemen, Rep.':'Republic of Yemen',
}

def get_df_old(subdir, fname):
    df = pd.read_csv(pjoin('data', subdir, fname), header=2).iloc[:,:-3].dropna()
    df = df.set_index(df['Country Name']).loc[:,'1960':]
    df.index = df.index.map(lambda c: c if c not in countries_replacement \
                                else countries_replacement[c])
    df = df.loc[sorted(set(df.index).difference(not_countries))]
    df.columns = df.columns.astype(int)
    print(df.shape)
    return df

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



def display_countries(series):
    for c in series:
        if c not in not_countries:
            if c in countries_replacement:
                print(countries_replacement[c])
            else:
                print(c)

def get_all_countries(dfs, index="name"):
    all_countries = sorted(list(set.intersection(*[set(dfs[key].index) for key in dfs])))
    if index == "name":
        all_countries = [c if c not in countries_replacement else countries_replacement[c]\
                        for c in all_countries if c not in not_countries]
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
    codes = get_all_countries(dfs, "code")
    dfs = unify_dfs(dfs, codes)
    names = []
    for iso3code in codes:
        country = pycountry.countries.get(alpha_3=iso3code)
        names.append(country.name)
    return dfs, dfs_continents, codes, names

if __name__ == "__main__":
    df_fertility = get_df('fertility-rate', 'API_SP.DYN.TFRT.IN_DS2_en_csv_v2_10474146.csv')
    df_life_expectancy = get_df('life-expectancy-at-birth', 'API_SP.DYN.LE00.IN_DS2_en_csv_v2_10473758.csv')
    df_population = get_df('population', 'API_SP.POP.TOTL_DS2_en_csv_v2_10473719.csv')
    df_birth_rate = get_df('birth-rate-crude', 'API_SP.DYN.CBRT.IN_DS2_en_csv_v2_10475710.csv')
    df_death_rate = get_df('death-rate-crude', 'API_SP.DYN.CDRT.IN_DS2_en_csv_v2_10474583.csv')
    display_countries(df_fertility.index)