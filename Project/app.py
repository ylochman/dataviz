import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import numpy as np
import pandas as pd

from data_utils import get_data
from app_utils import get_choropleth, get_histogram, get_general_plot
from app_utils import mapbox_access_token, scl1, scl2


# Data
dfs, dfs_continents, codes, names = get_data()
available_datatypes = {
    'fertility': "Fertility Rate",
    'life': "Life Expectancy",
    'population': "Population",
    'birth': "Birth Rate",
    'death': "Death Rate"
}
descriptions = {
    'fertility': """
    Fertility Rate is the number of children that would be born to a woman if
    she were to live to the end of her childbearing years and
    bear children in accordance with age-specific fertility
    rates of the specified year.
    """,
    'life': """
    Life Expectancy is the number of years a newborn infant would live if prevailing
    patterns of mortality at the time of its birth were to stay the
    same throughout its life.
    """,
    'population': """
    Population counts all residents regardless of legal status or
    citizenship. The values are midyear estimates.
    """,
    'birth': """
    Birth Rate is the number of live births occurring during the year,
    per 1,000 population estimated at midyear.
    """,
    'death': """
    Death Rate is the number of deaths occurring during the year,
    per 1,000 population estimated at midyear.
    """
}

# Text
title = html.H1("World Demography")
subtitle = html.Div([html.P(
    """Demographic situation in the 185 countries over the last 50 years."""),
    html.Br()])
source = dcc.Markdown(children=[
    "Source: [World Bank Open Data](https://data.worldbank.org)"
])
description = html.P(id="description")
# Customizing graphs
# Datatype
datatype_dropdown = html.Div([
    dcc.Dropdown(
        id='datatype_dropdown',
        options=[{'label': available_datatypes[i], 'value': i} for i in available_datatypes.keys()],
        value='fertility'
    )])

# Log Scale
logscale_flag = html.Div([dcc.Checklist(
        id='logscale_flag',
        options=[{'label': 'Logarithmic scale', 'value': 1},],
        values=[1])], style={
            'font-family': "Open Sans Light",
            'display': 'inline-block',
    })
# Years
playbutton = html.Button(children='Play', id='playbutton', title="right", style={
    'display': 'inline-block',
    "margin-right": "1em",
    })
years_slider = dcc.Slider(id='years_slider',
        min=1960, max=2016, value=1960, step=1,
        marks={str(year): str(year) for year in np.arange(1960,2020,10)})
# General-Plot
general_plot = dcc.Graph(id='general_plot')
# Choropleth Map
choropleth = dcc.Graph(id='choropleth')
# Histogram
histogram = dcc.Graph(id='histogram')

# Blocks
subblock = html.Div(
    className="row",
    children=[
        datatype_dropdown,
        html.Br(),
        description,
        html.Br(),
        html.Div([playbutton, logscale_flag], style={'display': 'inline-block'}),
        html.Br(),
        general_plot,
        html.Br(),
        years_slider
    ],
)
first_block = html.Div(
    className="four columns div-user-controls",
    children=[
        title,
        subtitle,
        subblock,
        dcc.Interval(
            id='interval',
            interval=500, # in milliseconds
            n_intervals=0),
        html.Br(),
        html.Br(),
        html.Div(id="aggregation"),
        html.Br(),
        source
    ]
)
second_block = html.Div(
    className="eight columns div-for-charts bg-grey",
    children=[
        choropleth,
        html.P(id="distribution", className="text-padding"),
        histogram
    ],
)
# Dash App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{"content": "width=device-width"}])
app.layout = html.Div(className="row", children=[first_block, second_block])

# Main Callback
@app.callback(
    [Output('general_plot', 'figure'),
     Output('choropleth', 'figure'),
     Output('histogram', 'figure')],
    [Input('datatype_dropdown', 'value'),
     Input('logscale_flag', 'values'),
     Input('years_slider', 'value')])
def update_figures(datatype, logscale_flag, year):
    zmin = dfs[datatype].loc[codes, :].min().min()
    zmax = dfs[datatype].loc[codes, :].max().max()
    z_values = dfs[datatype].loc[codes, year]
    mean_values = dfs[datatype].loc[codes, :].mean(0)
    if logscale_flag == [1]:
        z_values = np.log(z_values)
        mean_values = np.log(mean_values)
        zmin = np.log(zmin)
        zmax = np.log(zmax)
    colorscale = scl2 if datatype=='life' else scl1
    return get_general_plot(mean_values, colorscale, year),\
           get_choropleth(z_values, codes, names, colorscale, zmin, zmax),\
           get_histogram(z_values, 'doane', colorscale, zmin, zmax)

@app.callback(
    [Output('aggregation', 'children'),
     Output('distribution','children')],
    [Input('datatype_dropdown', 'value'),
     Input('logscale_flag', 'values'),
     Input('years_slider', 'value')])
def update_aggregation(datatype, logscale_flag, year):
    valuename = available_datatypes[datatype].lower()
    df = dfs[datatype].loc[codes, year]
    df_c = dfs_continents[datatype].loc[:, year]
    log_string = ""
    if logscale_flag == [1]:
        df = np.log(df)
        df_c = np.log(df_c)
        log_string = " (log)"
    if datatype in ("population"):
        agg_string = [html.P(children="Total world {}{}: {:,d}".format(valuename, log_string, int(df.sum())))]
        for row in df_c.sort_values(ascending=False).iteritems():
            agg_string.append(html.P(style={'marginLeft': 20},
                                     children="- {}:  {:,d}".format(row[0], int(row[1]))))
    else:
        agg_string = [html.P(children="Median world {}{}: {:.2f}".format(valuename, log_string, df.median()))]
        for row in df_c.sort_values(ascending=True).iteritems():
            agg_string.append(html.P(style={'marginLeft': 20},
                                     children="- {}:  {:.2f}".format(row[0], row[1])))
    return agg_string, ['Distribution of the {} accross the world'.format(valuename)]

@app.callback(
    Output('description', 'children'),
    [Input('datatype_dropdown', 'value')])
def update_description(datatype):
    return descriptions[datatype]

@app.callback(
    [Output('playbutton', 'children'),
    Output('years_slider', 'value'),
    Output('playbutton', 'title')],
    [Input('interval', 'n_intervals'),
     Input('playbutton', 'n_clicks')],
    [State('years_slider', 'value'),
    State('playbutton', 'title')])
def update_button(n, value, year, buttontitle):
    if value is None or value % 2 == 0: #currently pause
        return 'Play', year, buttontitle
    else:
        if buttontitle == "left":
            if year > 1960:
                year -= 1
            else:
                buttontitle = "right"
                year += 1
        else:
            if year < 2016:
                year += 1
            else:
                buttontitle = "left"
                year -= 1
        return 'Pause', year, buttontitle

# app.layout = html.Div([
#     html.Div([

#         html.Div([
#             dcc.Dropdown(
#                 id='xaxis-column',
#                 options=[{'label': i, 'value': i} for i in available_indicators],
#                 value='Fertility rate, total (births per woman)'
#             ),
#             dcc.RadioItems(
#                 id='xaxis-type',
#                 options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
#                 value='Linear',
#                 labelStyle={'display': 'inline-block'}
#             )
#         ],
#         style={'width': '48%', 'display': 'inline-block'}),

#         html.Div([
#             dcc.Dropdown(
#                 id='yaxis-column',
#                 options=[{'label': i, 'value': i} for i in available_indicators],
#                 value='Life expectancy at birth, total (years)'
#             ),
#             dcc.RadioItems(
#                 id='yaxis-type',
#                 options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
#                 value='Linear',
#                 labelStyle={'display': 'inline-block'}
#             )
#         ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
#     ]),


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8050)