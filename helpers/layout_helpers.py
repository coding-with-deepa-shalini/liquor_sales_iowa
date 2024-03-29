import os
import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc
from dateutil.relativedelta import relativedelta

import utils
from . import data_transformation

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)
df = data_transformation.transform_sales_data_overview(raw_df)

# parameters for date-picker
start_date = min(df['Date'])
end_date = pd.Timestamp(start_date.date() + relativedelta(months=+3))

# values for dropdown menus
liquor_types = utils.get_unique_values(df, "liquor_type")
counties = utils.get_unique_values(df, "county")
cities = utils.get_unique_values(df, "city")
category_names = utils.get_unique_values(df, "category_name")
vendor_names = utils.get_unique_values(df, "vendor_name")

def insights_get_subheader(settings_btn_id):
    insights_subheader = dbc.Row([
        dbc.Col([], width=1),
        dbc.Col([
            html.Div(
                dcc.Link(
                    "Overview",
                    href="/sales-overview",
                    style={'font-size': "21px"}
                )
            ),
            html.Div(
                dcc.Link(
                    "Sales by Store",
                    href="/sales-by-store",
                    style={'font-size': "21px"}
                )
            ),
            html.Div(
                dcc.Link(
                    "Sales by Liquor type",
                    href="/sales-by-liquor-type",
                    style={'font-size': "21px"}
                )
            )], width=5, className="d-flex align-content-center flex-wrap justify-content-evenly"),

            dbc.Col([
                html.A(
                    html.Img(id=settings_btn_id,
                        src="assets/settings-icon.svg", height="45px"
                    )
                )
            ], width=5, className="d-flex justify-content-end"),
            dbc.Col([], width=1)
        ], 
        className="bg-secondary"
    )

    return insights_subheader

def eda_get_subheader(info_btn_id):
    eda_subheader = dbc.Row([ 
        dbc.Col([], width=1),
        dbc.Col([
            html.Div(
                dcc.Link(
                    "Days of Week",
                    href="/days-of-week",
                    style={'font-size': "21px"}
                )
            ),
            html.Div(
                dcc.Link(
                    "Bivariate Trends",
                    href="/bivariate-trends",
                    style={'font-size': "21px"}
                )
            ),
            html.Div(
                dcc.Link(
                    "Prices",
                    href='/prices',
                    style={'font-size': "21px"}
                )
            )
            ], width=5, className="d-flex align-content-center flex-wrap justify-content-evenly"),

            dbc.Col([
                html.A(
                    html.Img(id=info_btn_id,
                        src="assets/information-icon.svg", height="45px"
                    )
                )
            ], width=5, className="d-flex justify-content-end"),
            dbc.Col([], width=1)
        ], className="bg-secondary"
    )

    return eda_subheader

def forecasting_get_subheader(info_btn_id):
    forecasting_subheader = dbc.Row([
        dbc.Col([], width=1),
        dbc.Col([
            html.Div(
                dcc.Link(
                    "Forecast",
                    href="/forecast",
                    style={'font-size': "21px"}
                )
            ),
            html.Div(
                dcc.Link(
                    "Forecast Trends",
                    href="/forecast-trends",
                    style={'font-size': "21px"}
                )
            ),
            ], width=5, className="d-flex align-content-center flex-wrap justify-content-evenly"),

            dbc.Col([
                html.A(
                    html.Img(id=info_btn_id,
                        src="assets/information-icon.svg", height="45px"
                    )
                )
            ], width=5, className="d-flex justify-content-end"),
            dbc.Col([], width=1)
        ], 
        className="bg-secondary"
    )

    return forecasting_subheader

# Common Insights settings
date_picker_range = dcc.DatePickerRange(
                id="date-picker-range",
                start_date = start_date,
                min_date_allowed = min(df["Date"]),
                end_date = end_date,
                max_date_allowed = max(df["Date"]),
                persistence=True, persistence_type="local"
            )

county_dropdown = dcc.Dropdown(
                id="dropdown-county",
                options=counties,
                placeholder="Select county",
                multi=True,
                persistence=True, persistence_type="local"
            )

city_dropdown = dcc.Dropdown(
                id="dropdown-city",
                options=cities,
                placeholder="Select city",
                multi=True,
                persistence=True, persistence_type="local"
            )

category_dropdown = dcc.Dropdown(
                id="dropdown-category-name",
                options=category_names,
                placeholder="Select category name",
                multi=True,
                persistence=True, persistence_type="local"
            )

vendor_dropdown = dcc.Dropdown(
                id="dropdown-vendor-name",
                options=vendor_names,
                placeholder="Select vendor name",
                multi=True,
                persistence=True, persistence_type="local"
            )

def get_alert(alert_id):
    insights_alert = dbc.Alert(
                "Option selected is not relevant due to the other filter selections",
                id=alert_id,
                is_open=False,
                color='danger'
            )

    return insights_alert

def get_positioned_alert(alert_id):
    pos_alert = dbc.Alert(
                "Option selected is not relevant due to the other filter selections",
                id=alert_id,
                is_open=False,
                color='danger',
                style={"position": "fixed", "top": 70, "right": 10, "width": 350},
            )

    return pos_alert

# Common components for EDA
def radio_items_for_y_axis(radio_items_id):    
    radio_items = dbc.RadioItems(
                            options=[
                                {"label": "Bottles sold", "value": "bottles_sold"},
                                {"label": "Sale (in dollars)", "value": "sale_dollars"},
                                {"label": "Volume sold (in litres)", "value": "volume_sold_liters"},
                                {"label": "State bottle cost", "value": "state_bottle_cost"},
                                {"label": "State bottle retail", "value": "state_bottle_retail"}
                            ],
                            value='state_bottle_cost',
                            id=radio_items_id,
                            persistence=True, persistence_type="local"
                        )
    
    return radio_items

# Common cards/parameters for Forecasting
model_parameters_card = dbc.Card([ 
                            dbc.CardHeader(html.H5("Parameters to tune model", className="card-title")),
                            dbc.CardBody([ 
                                html.P("Variable to forecast"),

                                dbc.RadioItems(
                                    options=[
                                        {"label": "Bottle sold", "value": "bottles_sold"},
                                        {"label": "Volume sold (in litres)", "value": "volume_sold_liters"}
                                    ],
                                    value="bottles_sold",
                                    id='radio-items-var-forecast',
                                    persistence=True, persistence_type="local"
                                ),

                                html.Hr(),

                                html.P("Number of months to predict", className="card-text"),

                                dbc.Input(
                                    type='number', min=1, max=24, value=12,
                                    id='number-of-months-to-predict',
                                    persistence=True, persistence_type="local"
                                ),

                                html.Br(),

                                html.P("Confidence interval (%)", className="card-text"),

                                dcc.Slider(
                                    min=80, max=99, value=95,
                                    marks=None,
                                    id='confidence-interval-slider',
                                    tooltip={"placement": "bottom", "always_visible": True},
                                    persistence=True, persistence_type="local"
                                ),

                                dbc.Switch(
                                    id='weekly-seasonality-switch', 
                                    label='Weekly Seasonality',
                                    value=True,
                                    persistence=True, persistence_type="local"
                                ),

                                dbc.Switch(
                                    id='monthly-seasonality-switch', 
                                    label='Monthly Seasonality',
                                    value=True,
                                    persistence=True, persistence_type="local"
                                ),

                                dbc.Switch(
                                    id='yearly-seasonality-switch', 
                                    label='Yearly Seasonality',
                                    value=True,
                                    persistence=True, persistence_type="local"
                                ),

                                dbc.Switch(
                                    id='holidays-switch',
                                    label='Factor in US holidays in model',
                                    value=True,
                                    persistence=True, persistence_type="local"
                                )
                            ])
                        ], color="secondary", outline=True)

filter_training_set_card = dbc.Card([ 
    dbc.CardHeader(html.H5("Filter training dataset"), className="card-title"),
    dbc.CardBody([
        dcc.Dropdown(
            id="dropdown-type-name-forecasting",
            options=liquor_types,
            placeholder="Select liquor types",
            value=["Schnapps"],
            multi=True,
            persistence=True, persistence_type="local"
        ),

        html.Br(),

        dcc.Dropdown(
            id="dropdown-vendor-name-forecasting",
            options=vendor_names,
            placeholder="Select vendors",
            multi=True,
            persistence=True, persistence_type="local"
        ),
    ])
], color="secondary", outline=True, className="mt-2")