import os
import dash
import random
import pandas as pd
import plotly.express as px
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
# set token to use Mapbox API
px.set_mapbox_access_token(open(os.path.join(DATAPATH, ".mapbox_token")).read())

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)
df = data_transformation.transform_sales_data_by_store(raw_df)

layout = html.Div([ 
    layout_helpers.get_subheader("btn-settings-by-store"),   
    dbc.Tooltip(
        "Settings",
        target="btn-settings-by-store"
    ),

    html.Div([
        dbc.Row([ 
            dbc.Col([                                 
                dbc.Switch(
                    id="light-switch",
                    label="Dark",
                    value=False,
                ),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                html.Hr(),
                dbc.Label("Values in choropleth and bar charts"),
                dbc.RadioItems(
                    id="radio-items-bubble-bar-value",
                    options=[
                        {'label': 'Bottles sold', 'value': 'bottles_sold'},
                        {'label': 'Sale ($)', 'value': 'sale_dollars'},
                        {'label': 'Volume sold (in litres)', 'value': 'volume_sold_liters'}
                    ],
                    value='sale_dollars',
                    labelStyle={'display': 'block'},
                    inputCheckedClassName="border border-success bg-success",
                    persistence=True, persistence_type="local"
                ),
            ], width=2, className="mt-5 ms-5"),
            dbc.Col([ 
                dbc.Spinner([dcc.Graph(id="choropleth-by-store")], color="primary")
            ], width=9, className="me-5")            
        ]),

        dbc.Row([
            dbc.Col([
                html.Hr(),
                dbc.Label("X-axis"),
                dbc.RadioItems( 
                    id="radio-items-x-city-county",
                    options=[
                        {'label': 'City', 'value': 'city'},
                        {'label': 'County', 'value': 'county'}
                    ],
                    value='city',
                    labelStyle={'display': 'block'},
                    inputCheckedClassName="border border-success bg-success",
                    persistence=True, persistence_type="local"
                )
            ], width=2, className="ms-5"),
            dbc.Col([ 
                dbc.Spinner([dcc.Graph(id="bar-chart-by-city-county")], color="primary")
            ], width=9, className="me-5")
        ])      
    ]),

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
    Input("dropdown-vendor-name", "value"),
    Input("radio-items-bubble-bar-value", "value"),
    Input("light-switch", "value")]
)
def update_scatter_mapbox(start_date, end_date, county_dropdown, city_dropdown, category_dropdown, vendor_dropdown, radio_bubble_bar_value, light_switch_value):

    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, category_dropdown, "category_name")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    transformed = final.groupby(['store_name', 'address', 'city', 'lat', 'lon'])[radio_bubble_bar_value].sum().reset_index(name='value')

    fig = px.scatter_mapbox(transformed, lat="lat", lon="lon", size='value',
                  size_max=20, zoom=5.8, height=450)
    
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=30))

    if (light_switch_value):
        fig.update_layout(mapbox_style='dark')
    
    else:
        fig.update_layout(mapbox_style='light')

    '''random.seed(1)

    category_intervals = pd.cut(transformed['value'], bins=bins_value, right=False).unique().tolist()
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
        df_sub = transformed[cat[0]:cat[1]]
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lon = df_sub['lon'],
            lat = df_sub['lat'],
            text = radio_bubble_bar_value + ": " + df_sub['value'].astype(str) + "<br>" + "Store: " + df_sub['store_name'] + "<br>" + 
                "Address: " + df_sub['address'] + "<br>" + "City: " + df_sub['city'],
            marker = dict(
                size = df_sub['value'],
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
            height=450,
            geo = dict(
                scope = 'usa',
                landcolor = 'rgb(255, 255, 255)'
            ),
            margin=dict(l=0,r=0,b=0,t=30)
        )'''

    return fig

@callback(Output("bar-chart-by-city-county", "figure"),
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("dropdown-county", "value"),
    Input("dropdown-city", "value"),
    Input("dropdown-category-name", "value"),
    Input("dropdown-vendor-name", "value"),
    Input("radio-items-bubble-bar-value", "value"),
    Input("radio-items-x-city-county", "value")]
)
def update_bar_chart(start_date, end_date, county_dropdown, city_dropdown, category_dropdown, vendor_dropdown, radio_bubble_bar_value, radio_items_bar_chart_x):

    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, category_dropdown, "category_name")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    bar_chart_df = final.groupby([radio_items_bar_chart_x])[radio_bubble_bar_value].sum().round(2).reset_index(name='value')
    bar_chart_df.sort_values(by=['value'], ascending=False, inplace=True)

    fig = px.bar(bar_chart_df, x=radio_items_bar_chart_x, y='value', height=350)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
                        margin=dict(l=0,r=0,b=0,t=0))

    return fig

'''html.Div([
        dash_table.DataTable(id="data-table-by-store",
            page_size=7,
            style_table={'overflowY': 'auto'},
            style_header={
                'whiteSpace': 'normal',
                'height': 'auto',
                'fontWeight': 'bold'
            },
            style_cell={
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0
            },
        )
    ], className="ms-5 me-5"),
    
    transformed1 = final.groupby(['store_name', 'address', 'city', 'county'])['bottles_sold'].sum().round(2).reset_index(name='value')
    transformed1.sort_values('value', ascending=False, inplace=True, ignore_index=True)
    transformed1.rename(columns={'value': 'Bottles sold'}, inplace=True)

    transformed2 = final.groupby(['store_name', 'address', 'city', 'county'])['sale_dollars'].sum().round(2).reset_index(name='value')
    transformed2.sort_values('value', ascending=False, inplace=True, ignore_index=True)
    transformed2.rename(columns={'value': "Sale ($)"}, inplace=True)

    merged = pd.merge(transformed1, transformed2, on='store_name')
    merged.rename(columns={'store_name': 'Store name', 'address_y': 'Address', 'city_y': 'City', 'county_y': 'County'}, inplace=True)

    # data table returns
    data=merged.to_dict('records')

    columns=list()
    columns.append({'name': 'Store name', 'id': 'Store name'})
    columns.append({'name': 'Address', 'id': 'Address'})
    columns.append({'name': 'City', 'id': 'City'})
    columns.append({'name': 'County', 'id': 'County'})
    columns.append({'name': 'Bottles sold', 'id': 'Bottles sold'})
    columns.append({'name': 'Sale ($)', 'id': 'Sale ($)'})

    style_data_table_conditional = (
        utils.data_bars(merged, 'Bottles sold', '#808080') +
        utils.data_bars(merged, 'Sale ($)', '#7261AC')
    )'''

'''dbc.Label("Bin values into categories"),
                dbc.Input(
                    id="input-bins-bubble-map",
                    type="number", min=0, max=20, step=1,
                    value=9,
                    persistence=True, persistence_type="local"
                ),
                dbc.Label("(The number of categories selected by the user may or may not be the same as that displayed in the Bubble chorepleth chart)"),'''
