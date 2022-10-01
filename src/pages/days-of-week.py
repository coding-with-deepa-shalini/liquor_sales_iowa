import os
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
from dash_bootstrap_templates import load_figure_template

import utils
from helpers import layout_helpers, data_transformation

dash.register_page(
    __name__,
    path='/days-of-week',
    title="Iowa Liquor Sales",
    name="Days of Week"
)

load_figure_template("pulse")

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data")

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)
df = data_transformation.transform_sales_data_eda(raw_df)

layout = html.Div([ 
    layout_helpers.eda_get_subheader("eda-days-of-week-info-btn"),
    dbc.Tooltip("Information", target="eda-days-of-week-info-btn"),

    html.Br(),
    dbc.Row([ 
        dbc.Col([ 
            dbc.Card(
                dbc.CardBody([ 
                    html.H6("Y-axis", className="card-title"),

                    layout_helpers.radio_items_for_y_axis('radio-days-of-week-row1'),

                    html.Hr(),

                    html.H6("Filter data", className="card-title"),

                    dcc.Dropdown(
                        id='eda-days-of-week-row1-dropdown-type',
                        options=utils.get_unique_values(df, 'liquor_type'),
                        placeholder="Select Liquor type",
                        multi=True,
                        persistence=True, persistence_type="local"
                    ),

                    dcc.Dropdown(
                        id='eda-days-of-week-row1-dropdown-county',
                        options=utils.get_unique_values(df, 'county'),
                        placeholder="Select county",
                        multi=True,
                        persistence=True, persistence_type="local"
                    ),

                    dcc.Dropdown(
                        id='eda-days-of-week-row1-dropdown-vendor',
                        options=utils.get_unique_values(df, 'vendor_name'),
                        placeholder="Select vendor",
                        multi=True,
                        persistence=True, persistence_type="local"
                    )
                ])
            )
        ], width=2, className="ms-3 dbc"),

        dbc.Col([ 
            dbc.Spinner(children=[dcc.Graph(id='eda-days-of-week-row1-graph1')], color='primary')
        ], width=4, className="ms-3"),

        dbc.Col([ 
            dbc.Spinner(children=[dcc.Graph(id='eda-days-of-week-row1-graph2')], color='primary')
        ], width=5, className="ms-3")
    ]),

    dbc.Row([ 
        dbc.Col([ 
            dbc.Card(
                dbc.CardBody([ 
                    html.H6("Y-axis", className="card-title"),

                    layout_helpers.radio_items_for_y_axis('radio-days-of-week-row2'),

                    html.Hr(),

                    html.H6("Filter data", className="card-title"),

                    dcc.Dropdown(
                        id='eda-days-of-week-row2-year-month',
                        options=utils.get_unique_values(df, 'year_month'),
                        placeholder="Select month",
                        multi=True,
                        persistence=True, persistence_type="local"
                    ),

                    dcc.Dropdown(
                        id='eda-days-of-week-row2-dropdown-county',
                        options=utils.get_unique_values(df, 'county'),
                        placeholder="Select county",
                        multi=True,
                        persistence=True, persistence_type="local"
                    ),

                    dcc.Dropdown(
                        id='eda-days-of-week-row2-dropdown-vendor',
                        options=utils.get_unique_values(df, 'vendor_name'),
                        placeholder="Select vendor",
                        multi=True,
                        persistence=True, persistence_type="local"
                    )
                ])
            )
        ], width=2, className="ms-3 dbc"),

        dbc.Col([ 
            dcc.Loading(children=[dcc.Graph(id='eda-days-of-week-row2-graph')], type='graph')
        ], width=9, className="ms-3")
    ]),

    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Page Information")),
        dbc.ModalBody(
            dcc.Markdown('''
            This page gives a deep-dive into the weekly seasonality trends of the Iowa liquor sales data. 
            
            Trends can be investigated with more detail by using the filters available. 
            
            If an option is selected in any of the filters that is not available because the data is already filtered, the user will be notified of this with the help of an alert which will be visible on the top-right corner.
            ''')
        ),
    ],
    id="eda-days-modal",
    is_open=False
    ),

    layout_helpers.get_positioned_alert("eda-days-row1-alert"),
    layout_helpers.get_positioned_alert("eda-days-row2-alert")
])

@callback(Output("eda-days-modal", "is_open"),
    Input("eda-days-of-week-info-btn", "n_clicks"),
    State("eda-days-modal", "is_open")
)
def toggle_modal(n_clicks, is_open):
    if (n_clicks):
        return not is_open
    return is_open

@callback([Output("eda-days-of-week-row1-graph1", "figure"),
    Output("eda-days-of-week-row1-graph2", "figure"),
    Output("eda-days-row1-alert", "is_open")],
    [Input("radio-days-of-week-row1", "value"),
    Input("eda-days-of-week-row1-dropdown-type", "value"),
    Input("eda-days-of-week-row1-dropdown-county", "value"),
    Input("eda-days-of-week-row1-dropdown-vendor", "value")]
)
def update_row1(radio_items_groupby_value, dropdown_type, dropdown_county, dropdown_vendor):
    
    final = df
    final = utils.filter_df_by_dropdown_select(final, dropdown_type, "liquor_type")
    final = utils.filter_df_by_dropdown_select(final, dropdown_county, "county")
    final = utils.filter_df_by_dropdown_select(final, dropdown_vendor, "vendor_name")

    if (len(final.index) == 0):
        return dash.no_update, dash.no_update, True

    final_gb = final.groupby(['year_month', 'weekday'])[radio_items_groupby_value].sum().reset_index()

    fig1 = px.bar(final_gb, x='year_month', y=radio_items_groupby_value, color='weekday', height=400, color_discrete_sequence=px.colors.qualitative.Bold)

    days_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    fig2 = px.violin(final, x='weekday', y=radio_items_groupby_value, height=400)
    fig2.update_xaxes(categoryorder='array', categoryarray=days_order)

    return fig1, fig2, False

@callback([Output("eda-days-of-week-row2-graph", "figure"),
    Output("eda-days-row2-alert", "is_open")],
    [Input("radio-days-of-week-row2", "value"),
    Input("eda-days-of-week-row2-year-month", "value"),
    Input("eda-days-of-week-row2-dropdown-county", "value"),
    Input("eda-days-of-week-row2-dropdown-vendor", "value")]
)
def update_row2(radio_items_groupby_value, dropdown_month, dropdown_county, dropdown_vendor):
    
    final = df
    final = utils.filter_df_by_dropdown_select(final, dropdown_month, "year_month")
    final = utils.filter_df_by_dropdown_select(final, dropdown_county, "county")
    final = utils.filter_df_by_dropdown_select(final, dropdown_vendor, "vendor_name")

    if (len(final.index) == 0):
        return dash.no_update, True

    final_gb = final.groupby(['liquor_type', 'weekday'])[radio_items_groupby_value].sum().reset_index()
    final_gb.sort_values([radio_items_groupby_value], ascending=False, inplace=True)

    fig = px.bar(final_gb, x='liquor_type', y=radio_items_groupby_value, color='weekday', facet_col='weekday', template="minty", height=400)

    return fig, False

