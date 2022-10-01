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
    path='/bivariate-trends',
    title="Iowa Liquor Sales",
    name="Bivariate Trends"
)

load_figure_template("pulse")

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)

layout = html.Div([ 
    layout_helpers.eda_get_subheader("eda-bivariate-info-btn"),
    dbc.Tooltip("Information", target="eda-bivariate-info-btn"),

    html.Br(),

    dbc.Row([ 
        dbc.Col([ 
            dbc.Card([
                dbc.CardBody([
                    html.H6("Variables to plot in Scatter matrix"),
                    dbc.Checklist(
                        options=[ 
                            {"label": "Bottles sold", "value": "bottles_sold"},
                            {"label": "Sale (in dollars)", "value": "sale_dollars"},
                            {"label": "Volume sold (in litres)", "value": "volume_sold_liters"},
                            {"label": "State bottle cost", "value": "state_bottle_cost"},
                            {"label": "State bottle retail", "value": "state_bottle_retail"},
                            {"label": "Pack", "value": "pack"}
                        ],
                        value=['state_bottle_cost', 'state_bottle_retail', 'pack'],
                        id='checklist-scatter-matrix',
                        persistence=True, persistence_type="local"
                    ),
                    html.Hr(),
                    html.H6("Filter dataset"),                    

                    dcc.Dropdown(
                        id='eda-bivariate-dropdown-county',
                        options=utils.get_unique_values(df, 'county'),
                        placeholder="Select county",
                        multi=True,
                        persistence=True, persistence_type="local"
                    ),

                    dcc.Dropdown(
                        id='eda-bivariate-dropdown-city',
                        options=utils.get_unique_values(df, 'city'),
                        placeholder="Select city",
                        multi=True,
                        persistence=True, persistence_type="local"
                    ),

                    dcc.Dropdown(
                        id='eda-bivariate-dropdown-vendor',
                        options=utils.get_unique_values(df, 'vendor_name'),
                        placeholder="Select vendor",
                        multi=True,
                        persistence=True, persistence_type="local"
                    ),
                ])
            ])
        ], width=2, className="ms-3 dbc"),

        dbc.Col([ 
            dbc.Spinner(children=[dcc.Graph(id='scatter-matrix-graph')], color='primary')
        ], width=9, className="ms-3")
    ]),

    dbc.Row([ 
        dbc.Col([ 
            dbc.Card(
                dbc.CardBody([
                    html.H6("X-axis", className="card-title"),
                    
                    dbc.RadioItems(
                        options=[ 
                            {"label": "Bottles sold", "value": "bottles_sold"},
                            {"label": "Volume sold (in litres)", "value": "volume_sold_liters"},
                            {"label": "Pack", "value": "pack"},
                        ],
                        value="pack",
                        id='radio-items-heatmap-x',
                        persistence=True, persistence_type="local"
                    ),

                    html.P("Number of bins"),

                    dcc.Slider(
                        min=5, max=25, value=10,
                        marks=None,
                        id='heatmap-bins-x',
                        tooltip={"placement": "bottom", "always_visible": True},
                        persistence=True, persistence_type="local"
                    ),

                    html.Hr(),

                    html.H6("Y-axis", className="card-title"),

                    dbc.RadioItems(
                        options=[ 
                            {"label": "Sale (in dollars)", "value": "sale_dollars"},
                            {"label": "State bottle cost", "value": "state_bottle_cost"},
                            {"label": "State bottle retail", "value": "state_bottle_retail"}
                        ],
                        value="state_bottle_retail",
                        id='radio-items-heatmap-y',
                        persistence=True, persistence_type="local"
                    ),

                    html.P("Number of bins"),

                    dcc.Slider(
                        min=5, max=25, value=10,
                        marks=None,
                        id='heatmap-bins-y',
                        tooltip={"placement": "bottom", "always_visible": True},
                        persistence=True, persistence_type="local"
                    )
                ])                
            )
        ], width=2, className="ms-3 dbc"),

        dbc.Col([
            dcc.Dropdown(
                options=utils.get_unique_values(df, "liquor_type"), value="Rum",
                id='heatmap-type-dropdown',
                persistence=True, persistence_type="local"
            ), 
            dbc.Spinner(children=[dcc.Graph(id='eda-bivariate-heatmap')], color='primary')
        ], width=9, className="ms-3")
    ]),

    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Page Information")),
        dbc.ModalBody(
            dcc.Markdown('''
            This page gives a correlation information of any two numerical parameters of the Iowa liquor sales data.

            Trends can be investigated with more detail by using the filters available.

            If an option is selected in any of the filters that is not available because the data is already filtered, the user will be notified of this with the help of an alert which will be visible on the top-right corner.
            ''')
        ),
    ],
    id="eda-bivariate-modal",
    is_open=False
    ),

    layout_helpers.get_positioned_alert("eda-bivariate-alert")
])

@callback(Output("eda-bivariate-modal", "is_open"),
    Input("eda-bivariate-info-btn", "n_clicks"),
    State("eda-bivariate-modal", "is_open")
)
def toggle_modal(n_clicks, is_open):
    if (n_clicks):
        return not is_open
    return is_open

@callback([Output("scatter-matrix-graph", "figure"),
    Output("eda-bivariate-alert", "is_open")],
    [Input("checklist-scatter-matrix", "value"),
    Input("eda-bivariate-dropdown-county", "value"),
    Input("eda-bivariate-dropdown-city", "value"),
    Input("eda-bivariate-dropdown-vendor", "value")]
)
def update_scatter_matrix(checklist_values, dropdown_county, dropdown_city, dropdown_vendor):

    final = df 
    final = utils.filter_df_by_dropdown_select(final, dropdown_county, "county")
    final = utils.filter_df_by_dropdown_select(final, dropdown_city, "city")
    final = utils.filter_df_by_dropdown_select(final, dropdown_vendor, "vendor_name")

    if (len(final.index) == 0):
        return dash.no_update, True

    return px.scatter_matrix(final, dimensions=checklist_values, color='liquor_type', color_discrete_sequence=px.colors.qualitative.Bold, height=400), False

@callback(Output("eda-bivariate-heatmap", "figure"),
    [Input("radio-items-heatmap-x", "value"),
    Input("heatmap-bins-x", "value"),
    Input("radio-items-heatmap-y", "value"),
    Input("heatmap-bins-y", "value"),
    Input("heatmap-type-dropdown", "value")]
)
def update_heatmap(heatmap_x, bins_x, heatmap_y, bins_y, type_dropdown):

    final = df[df['liquor_type'] == type_dropdown]
    
    return px.density_heatmap(final, x=heatmap_x, y=heatmap_y, nbinsx=int(round(bins_x)), nbinsy=int(round(bins_y)), height=400, template="pulse")