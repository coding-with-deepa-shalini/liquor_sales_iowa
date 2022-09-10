import os
import dash
import pandas as pd
import dash_bio as dashbio
import dash_bootstrap_components as dbc
from dash import html, dash_table, Input, Output, State, callback

import utils
from helpers import layout_helpers, circos_helpers, data_transformation

dash.register_page(
    __name__,
    path='/sales-overview',
    title="Iowa Liquor Sales",
    name="Sales Overview"
)

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)
df = data_transformation.transform_sales_data_overview(raw_df)

layout_config = {
    "labels": {"display": False},
    "ticks": {"display": False},
}

text_config = {
    "innerRadius": 260,   
    "style": {"font-size": 12, "font-weight": "bold"}  
}

dollars_heatmap_config = {
    "innerRadius": 200, 
    "outerRadius": 250, 
    "color": "Greens", 
    #"tooltipContent":{"source": "block_id", "target":"Date", "targetEnd":"value"}
}

volume_heatmap_config = {
    "innerRadius": 140, 
    "outerRadius": 190, 
    "color": "Greys", 
    #"tooltipContent":{"source": "block_id", "target":"Date", "targetEnd":"value"}
}

bottles_heatmap_config = {
    "innerRadius": 80, 
    "outerRadius": 130, 
    "color": "Purples", 
    #"tooltipContent":{"source": "block_id", "target":"Date", "targetEnd":"value"}
}

holidays_config = {
    "innerRadius": 50,
    "outerRadius": 70,
    "thickness": 20,
    "color": "red",
    "strokeWidth": 0,
    #"tooltipContent": {"source": "block_id", "target": "Date", "targetEnd": "holiday"}
}

layout = html.Div([
    layout_helpers.get_subheader("btn-settings-overview"),   
    dbc.Tooltip(
        "Settings",
        target="btn-settings"
    ),

    dbc.Row([

        # Calendar Circos graph
        dbc.Col([
            dashbio.Circos(id="calendar-circos",
            layout=[],
            tracks=[],
            config=layout_config,
            ),
        ], width=5),

        dbc.Col([
            html.Br(),
            html.Br(),
            html.Br(),

            # KPIs
            html.Div([
                dbc.Card([
                        dbc.Row([
                            dbc.Col([
                                dbc.CardImg(src="assets/checkout-icon.svg", className="img-fluid rounded-start")
                            ], className="col-md-4"),
                            dbc.Col([
                                dbc.CardBody([
                                    html.H5("Orders", className="text-secondary"),
                                    html.H2([], id="kpi-checkouts")
                                ])
                            ], className="col-md-8",)
                        ], className="g-0 d-flex align-items-center")
                    ], className="mb-3", style={"maxWidth": "540px"}),
                dbc.Card([
                        dbc.Row([
                            dbc.Col([
                                dbc.CardImg(src="assets/dollar-icon.svg", className="img-fluid rounded-start")
                            ], className="col-md-4"),
                            dbc.Col([
                                dbc.CardBody([
                                    html.H5("Sale in dollars", className="text-secondary"),
                                    html.H2([], id="kpi-gross-income")
                                ])
                            ], className="col-md-8",)
                        ], className="g-0 d-flex align-items-center")
                    ], className="mb-3", style={"maxWidth": "540px"}),
                dbc.Card([
                        dbc.Row([
                            dbc.Col([
                                dbc.CardImg(src="assets/units-icon.svg", className="img-fluid rounded-start")
                            ], className="col-md-4"),
                            dbc.Col([
                                dbc.CardBody([
                                    html.H5("Bottles Sold", className="text-secondary"),
                                    html.H2([], id="kpi-units-sold")
                                ])
                            ], className="col-md-8",)
                        ], className="g-0 d-flex align-items-center")
                    ], className="mb-3", style={"maxWidth": "540px"})
            ], className="d-flex justify-content-evenly"),

            html.Br(),           

            # Row for data table
            dbc.Row([
                 dash_table.DataTable(id="data-table-overview",
                    page_size=10,
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
                ),  

            # Legend for Calendar Circos
            dbc.Row([
                dbc.Col([
                    dbc.Badge("Sale (in dollars)", pill=True, color="success"),
                    dbc.Badge("Volume sold (in liters)", pill=True, color="dark"),
                    dbc.Badge("Bottles sold", pill=True, color="primary"),
                    dbc.Badge("Public holidays", pill=True, color="danger")
                    ], width=1),                 
                ]),
            ])                     
        ], width=6),       

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
            id="settings-menu-overview",
            is_open=False,            
        )          
    ])
])

@callback(
    Output("settings-menu-overview", "is_open"),
    Input("btn-settings-overview", "n_clicks"),
    [State("settings-menu-overview", "is_open")],
)
def toggle_settings_menu(n, is_open):
    if (n):
        return not is_open
    return is_open

@callback([Output("calendar-circos", "layout"),
    Output("calendar-circos", "tracks"),
    Output("kpi-checkouts", "children"),
    Output("kpi-gross-income", "children"),
    Output("kpi-units-sold", "children"),
    Output("data-table-overview", "data"),
    Output("data-table-overview", "columns"),
    Output("data-table-overview", "style_data_conditional")],
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

    # write json file and read it into a variable which will be used for Calendar Circos
    circos_helpers.write_circos_json(final)
    circos_data = circos_helpers.read_json(os.path.join(DATAPATH,"circos_data.json"))   

    # calendar circos returns
    layout = circos_data["calendar"]
    tracks = [
                {
                    "type": "HEATMAP",
                    "data": circos_data["income_histogram"],
                    "config": dollars_heatmap_config,
                },
                {
                    "type": "HEATMAP",
                    "data": circos_data["volume_histogram"],
                    "config": volume_heatmap_config,
                },
                {
                    "type": "HEATMAP",
                    "data": circos_data["sales_histogram"],
                    "config": bottles_heatmap_config,
                },
                {
                    "type": "TEXT",
                    "data": circos_data["text"],
                    "config": text_config
                },
                {
                    "type": "STACK",
                    "data": circos_data["holidays"],
                    "config": holidays_config
                }
            ]

    # KPI returns
    kpi1 = str(final.shape[0])
    kpi2 = final['sale_dollars'].sum().round(2).astype(str)
    kpi3 = final['bottles_sold'].sum().astype(str)

    # transform df for data table
    transformed1 = final.groupby(['category_name'])['sale_dollars'].sum().round(2).reset_index(name='value')
    transformed1.sort_values('value', ascending=False, inplace=True, ignore_index=True)
    transformed1.rename(columns={'value': 'Sale ($)'}, inplace=True)

    transformed2 = final.groupby(['category_name'])['bottles_sold'].sum().round(2).reset_index(name='value')
    transformed2.sort_values('value', ascending=False, inplace=True, ignore_index=True)
    transformed2.rename(columns={'value': "Bottles sold"}, inplace=True)

    merged = pd.merge(transformed1, transformed2, on='category_name')
    merged.rename(columns={'category_name': 'Category'}, inplace=True)

    # data table returns
    data=merged.to_dict('records')
    columns=[{"name": i, "id": i} for i in merged.columns]

    style_data_table_conditional = (
        utils.data_bars(merged, 'Bottles sold', '#808080') +
        utils.data_bars(merged, 'Sale ($)', '#7261AC')
    )
    
    return layout, tracks, kpi1, kpi2, kpi3, data, columns, style_data_table_conditional
