import os
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
from dash_bootstrap_templates import load_figure_template

import utils
from helpers import layout_helpers

dash.register_page(
    __name__,
    path='/prices',
    title="Iowa Liquor Sales",
    name="Prices"
)

load_figure_template("pulse")

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data")

df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)

types = utils.get_unique_values(df, "liquor_type")
types_radio_items = list()

for i in types:
    sub_list_keys = ['label', 'value']
    sub_list_values = [i, i]
    sub_dict = dict(zip(sub_list_keys, sub_list_values))
    types_radio_items.append(sub_dict)

layout = html.Div([ 
    layout_helpers.eda_get_subheader("eda-prices-info-btn"),
    dbc.Tooltip("Information", target="eda-prices-info-btn"),

    html.Br(),

    dbc.Row([ 
        dbc.Col([ 
            dbc.Card(
                dbc.CardBody([
                    html.H6("Liquor type", className="card-title"),

                    dbc.RadioItems(
                        options=types_radio_items,
                        value='Gin',
                        id='radio-type-prices-boxplots',
                        persistence=True, persistence_type="local"
                    ),

                    html.Hr(),

                    html.H6("X-axis", className="card-title"),

                    dbc.RadioItems(
                        options=[ 
                            {"label": "State bottle cost", "value": "state_bottle_cost"},
                            {"label": "State bottle retail", "value": "state_bottle_retail"}
                        ],
                        value='state_bottle_cost',
                        id='radio-x-axis-prices-boxplots',
                        persistence=True, persistence_type="local"
                    ),

                    html.Hr(),

                    html.H6("Filter dataset", className="card-title"),

                    dcc.Dropdown(
                        options=utils.get_unique_values(df, "county"),
                        id="prices-county-dropdown",
                        multi=True,
                        placeholder="Select county",
                        persistence=True, persistence_type="local"
                    ),

                    html.Br(),

                    dcc.Dropdown(
                        options=utils.get_unique_values(df, "city"),
                        id="prices-city-dropdown",
                        multi=True,
                        placeholder="Select city",
                        persistence=True, persistence_type="local"
                    ),

                    html.Br(),
                    html.P("Pack"),

                    dcc.RangeSlider(
                        min=min(utils.get_unique_values(df, "pack")),
                        max=max(utils.get_unique_values(df, "pack")),
                        value=[min(utils.get_unique_values(df, "pack")), max(utils.get_unique_values(df, "pack"))],
                        tooltip={"placement": "bottom", "always_visible": True},
                        id='prices-rangeslider-pack',
                        persistence=True, persistence_type="local"
                    )
                ])
            )
        ], width=2, className="ms-3 dbc"),

        dbc.Col([ 
            dbc.Spinner(children=[dcc.Graph(id='vendor-boxplot')], color='primary'),
            dbc.Spinner(children=[dcc.Graph(id='type-boxplot')], color='primary')
        ], width=9, className="ms-3")
    ]),

    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Page Information")),
        dbc.ModalBody(dcc.Markdown('''
            This page gives gives information about the variation in prices in liquor categories and vendors of the Iowa liquor sales data.

            Trends can be investigated with more detail by using the filters available.
            
            If an option is selected in any of the filters that is not available because the data is already filtered, the user will be notified of this with the help of an alert which will be visible on the top-right corner.
            ''')
        ),
    ],
    id="eda-prices-modal",
    is_open=False
    ),

    layout_helpers.get_positioned_alert("eda-prices-alert")
])

@callback(Output("eda-prices-modal", "is_open"),
    Input("eda-prices-info-btn", "n_clicks"),
    State("eda-prices-modal", "is_open")
)
def toggle_modal(n_clicks, is_open):
    if (n_clicks):
        return not is_open
    return is_open

@callback([Output("vendor-boxplot", "figure"),
    Output("type-boxplot", "figure"),
    Output("eda-prices-alert", "is_open")],
    [Input("radio-type-prices-boxplots", "value"),
    Input("radio-x-axis-prices-boxplots", "value"),
    Input("prices-county-dropdown", "value"),
    Input("prices-city-dropdown", "value"),
    Input("prices-rangeslider-pack", "value")]
)
def update_dashboard(type_selection, x_axis, county_dropdown, city_dropdown, pack_slider_value):

    final = df[(df["pack"] >= pack_slider_value[0]) & (df["pack"] <= pack_slider_value[1])]
    final = final[final['liquor_type'] == type_selection]
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")

    if (len(final.index) == 0):
        return dash.no_update, dash.no_update, True

    fig1 = px.box(final, x=x_axis, y="vendor_name", height=400, template="pulse")
    fig2 = px.box(final, x=x_axis, y="category_name", height=400, template="pulse")

    return fig1, fig2, False