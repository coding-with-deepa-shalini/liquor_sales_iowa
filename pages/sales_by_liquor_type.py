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
    path='/sales-by-liquor-type',
    title="Iowa Liquor Sales",
    name="Sales by Liquor Type"
)

load_figure_template("pulse")

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)
df = data_transformation.transform_sales_data_by_store(raw_df)

layout = html.Div([ 
    layout_helpers.insights_get_subheader("btn-settings-by-type"),   
    dbc.Tooltip(
        "Settings",
        target="btn-settings-by-type"
    ),

    html.Div([
        dbc.Row([ 
            dbc.Col([ 
                dbc.Spinner([dcc.Graph(id="treemap-by-type")], color="primary")
            ], width=7),
            dbc.Col([ 
                dbc.Spinner([dcc.Graph(id="sunburst-by-type")], color="primary")
            ], width=5)
        ]),

        dbc.Row([ 
            dbc.Col([
                dbc.Label("X-axis"),
                dbc.RadioItems(
                    id="radio-items-x-axis",
                    options=[
                        {'label': 'By day', 'value': 'Date'},
                        {'label': 'By week', 'value': 'week_start_date'},
                        {'label': 'By month', 'value': 'year_month'}
                    ],
                    value='week_start_date',
                    labelStyle={'display': 'block'},
                    inputCheckedClassName="border border-success bg-success",
                    persistence=True, persistence_type="local"
                ),
                html.Hr(),
                dbc.Label("Y-axis"),
                dbc.RadioItems(
                    id="radio-items-y-axis",
                    options=[
                        {'label': 'Bottles sold', 'value': 'bottles_sold'},
                        {'label': 'Sale ($)', 'value': 'sale_dollars'},
                        {'label': 'Volume sold (in litres)', 'value': 'volume_sold_liters'}
                    ],
                    value='bottles_sold',
                    labelStyle={'display': 'block'},
                    inputCheckedClassName="border border-success bg-success",
                    persistence=True, persistence_type="local"
                ),
            ], width=2, className="ms-5"),
            dbc.Col([ 
                dbc.Spinner([dcc.Graph(id="area-by-type")], color="primary")
            ], width=9)
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
        id="settings-menu-by-type",
        is_open=False,
        className="dbc"            
    )
])

@callback(
    Output("settings-menu-by-type", "is_open"),
    Input("btn-settings-by-type", "n_clicks"),
    [State("settings-menu-by-type", "is_open")],
)
def toggle_settings_menu(n, is_open):
    if (n):
        return not is_open
    return is_open

@callback([Output("treemap-by-type", "figure"),
    Output("sunburst-by-type", "figure")],
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("dropdown-county", "value"),
    Input("dropdown-city", "value"),
    Input("dropdown-category-name", "value"),
    Input("dropdown-vendor-name", "value")]
)
def update_row1(start_date, end_date, county_dropdown, city_dropdown, category_dropdown, vendor_dropdown):

    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, category_dropdown, "category_name")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    tree1 = final.groupby(['liquor_type', 'category_name'])['bottles_sold'].sum().reset_index(name='bottles_sold')
    tree2 = final.groupby(['liquor_type', 'category_name'])['sale_dollars'].sum().round(2).reset_index(name='sale_dollars')
    treemap_df = pd.merge(tree1, tree2, on=['liquor_type', 'category_name'])

    # color_continuous_scale="Aggrnyl"
    treemap = px.treemap(treemap_df, path=[px.Constant("Liquor type"), "liquor_type", "category_name"], 
        values="bottles_sold", color="sale_dollars", template="pulse")

    sunburst_df = final.groupby(['liquor_type', 'vendor_name'])['bottles_sold'].sum().reset_index(name='bottles_sold')
    sunburst = px.sunburst(sunburst_df, path=['liquor_type', 'vendor_name'], values='bottles_sold', template="pulse")

    return treemap, sunburst

@callback(Output("area-by-type", "figure"),
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("dropdown-county", "value"),
    Input("dropdown-city", "value"),
    Input("dropdown-category-name", "value"),
    Input("dropdown-vendor-name", "value"),
    Input("radio-items-x-axis", "value"),
    Input("radio-items-y-axis", "value")]
)
def update_row2(start_date, end_date, county_dropdown, city_dropdown, category_dropdown, vendor_dropdown, radio_items_x, radio_items_y):

    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, category_dropdown, "category_name")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    area_df = final.groupby(['liquor_type', radio_items_x])[radio_items_y].sum().round(2).reset_index(name=radio_items_y)
    area = px.area(area_df, x=radio_items_x, y=radio_items_y, color='liquor_type', height=350, template="pulse")
    area.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
                        margin=dict(l=0,r=0,b=0,t=0))

    return area