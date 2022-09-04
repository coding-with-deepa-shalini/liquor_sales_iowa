import os
import dash
import random
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, Input, Output, State, callback

import utils
from helpers import layout_helpers, data_transformation

dash.register_page(
    __name__,
    path='/sales-by-store',
    title="Iowa Liquor Sales",
    name="Sales by Store"
)

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal.csv"), index_col=False)
df = data_transformation.transform_sales_data(raw_df)

layout = html.Div([ 
    layout_helpers.get_subheader("btn-settings-by-store"),   
    dbc.Tooltip(
        "Settings",
        target="btn-settings"
    ),

    html.Div([ 
        dbc.Spinner([dcc.Graph(id="choropleth-by-store")], color="primary")
    ], className="ms-5 me-5"),

    # Settings menu
    dbc.Offcanvas([

        layout_helpers.date_picker_range,

        html.Br(),
        html.Br(),

        layout_helpers.county_dropdown,

        html.Br(),

        layout_helpers.city_dropdown,

        html.Br(),

        layout_helpers.category_dropdown,
            
        html.Br(),
            
        layout_helpers.vendor_dropdown
        ],

        title="Settings",
        placement="end",
        id="settings-menu-by-store",
        is_open=False,            
    )
])

@callback(
    Output("settings-menu-by-store", "is_open"),
    Input("btn-settings-by-store", "n_clicks"),
    [State("settings-menu-by-store", "is_open")],
)
def toggle_settings_menu(n, is_open):
    if (n):
        return not is_open
    return is_open

@callback(Output("choropleth-by-store", "figure"),
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("dropdown-county", "value"),
    Input("dropdown-city", "value"),
    Input("dropdown-category-name", "value"),
    Input("dropdown-vendor-name", "value")]
)
def update_dashboard(start_date, end_date, county_dropdown, city_dropdown, category_dropdown, vendor_dropdown):

    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, category_dropdown, "category_name")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    random.seed(1)

    category_intervals = pd.cut(df['bottles_sold'], bins=9, right=False).unique().tolist()
    # remove the nan
    category_intervals.pop()

    categories = []

    for i in range(len(category_intervals)):
        category = list()
        category.append(category_intervals[i].left.round().astype(int))
        category.append(category_intervals[i].right.round().astype(int))
        categories.append(tuple(category))

    number_of_colours = len(categories)

    colours = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                for i in range(number_of_colours)]

    fig = go.Figure()

    for i in range(len(categories)):
        cat = categories[i]
        df_sub = final[cat[0]:cat[1]]
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lon = df_sub['lon'],
            lat = df_sub['lat'],
            text = df_sub['store_number'].astype(str) + df_sub['store_name'] + "\n" + df_sub['address'] + "\n" + df_sub['city'],
            marker = dict(
                size = df_sub['bottles_sold'],
                color = colours[i],
                line_color='rgb(40,40,40)',
                line_width=0.5,
                sizemode = 'area'
            ),
            name = '{0} - {1}'.format(cat[0],cat[1])))

    fig.update_geos(fitbounds="locations", showsubunits=True, subunitcolor="#808080")
    fig.update_layout(
            #title_text = '2014 US city populations<br>(Click legend to toggle traces)',
            showlegend = True,
            height=600,
            geo = dict(
                scope = 'usa',
                landcolor = 'rgb(255, 255, 255)'
            )
        )

    return fig
