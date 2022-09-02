import os
import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc
from dateutil.relativedelta import relativedelta

import utils
from . import data_transformation

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal.csv"), index_col=False)
df = data_transformation.transform_sales_data(raw_df)

# parameters for date-picker
start_date = min(df['Date'])
end_date = pd.Timestamp(start_date.date() + relativedelta(months=+4))

# values for dropdown menus
#payment_types = utils.get_unique_values(df, "Payment")

insights_subheader = dbc.Row([
    dbc.Col([], width=1),
    dbc.Col([
        html.Div(
            dcc.Link(
                "Income Overview",
                href="/sales-overview",
                style={'font-size': "21px"}
            )
        ),
        html.Div(
            dcc.Link(
                "Income by Product Line",
                href="/sales-overview",
                style={'font-size': "21px"}
            )
        ),
        html.Div(
            dcc.Link(
                "Income by Branch",
                href="/sales-overview",
                style={'font-size': "21px"}
            )
        )], width=5, className="d-flex align-content-center flex-wrap justify-content-evenly"),

        dbc.Col([
            html.A(
                html.Img(id="btn-settings",
                    src="assets/settings-icon.svg", height="45px"
                )
            )
        ], width=5, className="d-flex justify-content-end"),
        dbc.Col([], width=1)
    ], 
    className="bg-secondary"
)

# Common settings
date_picker_range = dcc.DatePickerRange(
                id="date-picker-range",
                start_date = start_date,
                min_date_allowed = min(df["date"]),
                end_date = end_date,
                max_date_allowed = max(df["date"]),
                persistence=True, persistence_type="local"
            )