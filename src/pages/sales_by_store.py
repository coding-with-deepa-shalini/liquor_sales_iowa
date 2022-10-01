import os
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import dcc, html, Input, Output, State, callback

import utils
from helpers import layout_helpers, data_transformation

dash.register_page(
    __name__,
    path='/sales-by-store',
    title="Iowa Liquor Sales",
    name="Sales by Store"
)

load_figure_template("minty")

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data")
# set token to use Mapbox API
px.set_mapbox_access_token(open(os.path.join(DATAPATH, ".mapbox_token")).read())

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)
df = data_transformation.transform_sales_data_by_store(raw_df)

# title for bar chart
y_axis_dict = {'bottles_sold': 'Bottles sold', 'sale_dollars': 'Sales (in dollars)', 'volume_sold_liters': 'Volume sold (in litres)'}

layout = html.Div([ 
    layout_helpers.insights_get_subheader("btn-settings-by-store"),   
    dbc.Tooltip(
        "Settings",
        target="btn-settings-by-store"
    ),

    html.Br(),

    html.Div([
        dbc.Row([ 
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([ 
                        html.H6("Parameter to plot", className="card-title"),

                        dbc.RadioItems(
                            id="radio-items-bubble-value",
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

                        html.Br(),

                        html.P("Map background"),

                        dbc.Switch(
                            id="light-switch",
                            label="Dark",
                            value=False,
                        ),

                        html.Br(),

                        html.P("Marker colour"),

                        dbc.Input(
                            type='color',
                            id='scatter-map-marker-colour',
                            style={"width": 75, "height": 50}
                        ),

                        html.Br(),

                        html.Div([ 
                            dcc.RangeSlider(
                            min=[], max=[], value=[],
                            marks=None,
                            id="range-slider-scatter-values",
                            tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ]),
                    ])
                )            
            ], width=2, className="ms-3 dbc"),

            dbc.Col([ 
                dbc.Spinner([dcc.Graph(id="choropleth-by-store")], color="primary")
            ], width=9, className="ms-3")            
        ]),

        dbc.Row([
            dbc.Col([

                dbc.Card(
                    dbc.CardBody([ 
                        html.H6("X-axis", className="card-title"),

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
                        ),

                        html.Hr(),

                        html.H6("Y-axis", className="card-title"),

                        dbc.RadioItems(
                            id="radio-items-bar-value",
                            options=[
                                {'label': 'Bottles sold', 'value': 'bottles_sold'},
                                {'label': 'Sale ($)', 'value': 'sale_dollars'},
                                {'label': 'Volume sold (in litres)', 'value': 'volume_sold_liters'}
                            ],
                            value='sale_dollars',
                            labelStyle={'display': 'block'},
                            inputCheckedClassName="border border-success bg-success",
                            persistence=True, persistence_type="local"
                        )
                    ])
                )                
            ], width=2, className="ms-3"),

            dbc.Col([ 
                dbc.Spinner([dcc.Graph(id="bar-chart-by-city-county")], color="primary")
            ], width=9, className="ms-3")
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
            
        layout_helpers.vendor_dropdown,

        html.Br(),

        layout_helpers.get_alert("insights-store-alert")
        ],

        title="Settings",
        placement="end",
        id="settings-menu-by-store",
        is_open=False,
        className="dbc"            
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

@callback(Output("scatter-map-marker-colour", "value"),
    Input("light-switch", "value")
)
def update_colour_picker(dark_switch):
    if (dark_switch):
        return "#95DFC9"

    else:
        return "#191970"

@callback([Output("range-slider-scatter-values", "min"),
    Output("range-slider-scatter-values", "max"),
    Output("range-slider-scatter-values", "value")],
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("dropdown-county", "value"),
    Input("dropdown-city", "value"),
    Input("dropdown-category-name", "value"),
    Input("dropdown-vendor-name", "value"),
    Input("radio-items-bubble-value", "value")]
)
def update_range_slider(start_date, end_date, county_dropdown, city_dropdown, category_dropdown, vendor_dropdown, radio_bubble_value):
    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, category_dropdown, "category_name")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    if (len(final.index) == 0):
        return dash.no_update, dash.no_update, dash.no_update

    transformed = final.groupby(['store_name', 'address', 'city', 'lat', 'lon'])[radio_bubble_value].sum().reset_index(name='value')

    range_min = min(transformed['value'])
    range_max = max(transformed['value'])
    value = [range_min, range_max]

    return range_min, range_max, value


@callback([Output("choropleth-by-store", "figure"),
    Output("insights-store-alert", "is_open")],
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("dropdown-county", "value"),
    Input("dropdown-city", "value"),
    Input("dropdown-category-name", "value"),
    Input("dropdown-vendor-name", "value"),
    Input("radio-items-bubble-value", "value"),
    Input("light-switch", "value"),
    Input("scatter-map-marker-colour", "value"),
    Input("range-slider-scatter-values", "value")]
)
def update_scatter_mapbox(start_date, end_date, county_dropdown, city_dropdown, category_dropdown, vendor_dropdown, radio_bubble_value, light_switch_value, marker_colour, range_value):

    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, category_dropdown, "category_name")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    if (len(final.index) == 0):
        return dash.no_update, True

    transformed = final.groupby(['store_name', 'address', 'city', 'county', 'lat', 'lon'])[radio_bubble_value].sum().reset_index(name='value')

    # filter by ranger slider selection
    transformed = transformed[(transformed['value'] >= range_value[0]) & (transformed['value'] <= range_value[1])]

    mapbox_template = str()

    if (light_switch_value):
        mapbox_template = 'dark'

    else:
        mapbox_template = 'open-street-map' #open-street-map

    fig = px.scatter_mapbox(transformed, lat="lat", lon="lon", size='value',
                  size_max=20, zoom=5.8, height=450,              
                  color_discrete_sequence=[marker_colour],   
                  hover_data=["store_name", "value", "city", "county"])
    
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=30), mapbox_style=mapbox_template)

    return fig, False

@callback(Output("bar-chart-by-city-county", "figure"),
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("dropdown-county", "value"),
    Input("dropdown-city", "value"),
    Input("dropdown-category-name", "value"),
    Input("dropdown-vendor-name", "value"),
    Input("radio-items-bar-value", "value"),
    Input("radio-items-x-city-county", "value")]
)
def update_bar_chart(start_date, end_date, county_dropdown, city_dropdown, category_dropdown, vendor_dropdown, radio_bar_value, radio_items_bar_chart_x):

    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, category_dropdown, "category_name")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    if (len(final.index) == 0):
        return dash.no_update

    bar_chart_df = final.groupby([radio_items_bar_chart_x])[radio_bar_value].sum().round(2).reset_index(name='value')
    bar_chart_df.sort_values(by=['value'], ascending=False, inplace=True)

    fig = px.bar(bar_chart_df, x=radio_items_bar_chart_x, y='value', height=350, template="minty", title=y_axis_dict[radio_bar_value] + " by " + radio_items_bar_chart_x)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
                        margin=dict(l=0,r=0,b=0))

    return fig