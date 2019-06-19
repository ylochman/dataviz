import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import copy

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
main_colors = ['#FF3368', '#554DD2', '#5BEFA7', "orange"]
scl1 = [[0.0, main_colors[2]], [0.5, main_colors[1]], [1.0, main_colors[0]]]
scl2 = [[0.0, main_colors[0]], [0.5, main_colors[1]], [1.0, main_colors[2]]]

def get_choropleth(z_values, codes, names, colorscale, zmin, zmax):
    zoom = 12.0
    latInitial = 40.7272
    lonInitial = -73.991251

    choropleth_data = [go.Choropleth(
        geo="geo",
        colorscale=colorscale,
        autocolorscale=False,
        locations=codes,
        z=z_values,
        locationmode='ISO-3',
        text=names,
        hoverinfo="text+z",
        zmin=zmin,
        zmax=zmax,
        marker=go.choropleth.Marker(
                line=go.choropleth.marker.Line(color="#101010", width=0.5), # countroes borders
            ),
        colorbar = go.choropleth.ColorBar( # color bar
                    title="",
                    x=0.95,
                    xpad=0,
                    tickfont=dict(color="#d8d8d8"),
                    titlefont=dict(color="#d8d8d8"),
                    thickness=10,
                    thicknessmode="pixels",),
        )
    ]
    choropleth_layout = go.Layout(
                autosize=True,
                geo = dict(
                    showframe=False,
                    showcoastlines=True,
                    showland=True,
                    landcolor="#424140",
                    coastlinecolor="#101010",
                    coastlinewidth=0.5,
                    bgcolor="#222120"),
                margin={'l': 20, 'b': 20, 't': 20, 'r': 20},
                legend={'x': 0, 'y': 1},
                plot_bgcolor="#323130", paper_bgcolor="#323130",
                hovermode='closest')
    choropleth = {'data': choropleth_data, 'layout': choropleth_layout}
    return choropleth

def get_histogram(z_values, bins, colorscale, zmin, zmax):
    yVal, xVal = np.histogram(z_values, bins)
    histogram_data = [
                go.Bar(x=xVal, y=yVal, marker=dict(color=xVal, colorscale=colorscale, cmin=zmin, cmax=zmax), hoverinfo="x"),
                go.Scatter(
                    opacity=0,
                    x=xVal,
                    y=yVal / 2,
                    hoverinfo="none",
                    mode="markers",
                    marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                    visible=True,
                ),
            ]
    histogram_layout = go.Layout(
        autosize=True,
        height=400,
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin={'l': 10, 'b': 10, 't': 0, 'r': 10},
        showlegend=False,
        plot_bgcolor="#323130", paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="#323130"),
        xaxis=dict(
            range=[xVal[0], xVal[-1]],
            showgrid=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )
    histogram = {'data': histogram_data, 'layout': histogram_layout}
    return histogram

def get_general_plot(z_values, colorscale, year):
    xs = np.arange(1960,2017,1)
    ys = z_values.loc[xs]
    plot_data = [dict(
            type='scatter',
            mode='lines',
            x=xs, y=ys,
            colorscale=colorscale,
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                # colorscale=colorscale
            )),
        dict(
            type='scatter',
            mode='markers',
            x=[year],
            y=[z_values.loc[year]],
            line=dict(
                shape="spline",
                smoothing=2,
                width=1,
                color="#FF3368",
            )
            )
    ]
    plot_layout = dict(
        autosize=True,
        height=150,
        # width=500,
        # automargin=True,
        margin=dict(
            l=30,
            r=30,
            b=20,
            t=40
        ),
        hovermode="closest",
        showlegend=False,
        plot_bgcolor="#1E1E1E", paper_bgcolor="#1E1E1E", zoom=1,
        xaxis=dict(
            range=[1960, 2016],
            showticklabels=False,
            showgrid=False,
            showline=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[min(ys)*0.9, max(ys)*1.1],
            showticklabels=True,
            showgrid=True,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        )
    )
    general_plot = {'data': plot_data, 'layout': plot_layout}
    return general_plot