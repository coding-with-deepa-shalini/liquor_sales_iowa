import os
import dash
import pandas as pd
import dash_bio as dashbio
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, Input, Output, State, callback

import utils
from helpers import layout_helpers, circos_helpers, data_transformation

dash.register_page(
    __name__,
    path='/sales-overview',
    title="Iowa Liquor Sales",
    name="Sales Overview"
)

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal.csv"), index_col=False)
df = data_transformation.transform_sales_data(raw_df)

#table = df.groupby(by=['Date', 'Product line'])['Quantity'].sum().reset_index(name='value')
#transposed = table.pivot(index='date', columns='Product line', values='value').reset_index().rename_axis(None, axis=1)

'''holidays = pd.read_csv(os.path.join(DATAPATH,"holidays-myanmar.csv"), index_col=False)
holidays['date'] = pd.to_datetime(holidays['date'], format="%Y-%m-%d")
holidays['date'] = holidays['date'].dt.date
hols = holidays['date']'''

# values for dropdown menus
branches = utils.get_unique_values(df, "county")
product_lines = utils.get_unique_values(df, "category_name")

#data_table_title = {"Quantity": "Quantity of each product line sold daily", "Gross Income": "Gross income of each product line sold daily"}

layout_config = {
    "labels": {"display": False},
    "ticks": {"display": False},
}

text_config = {
    "innerRadius": 260,   
    "style": {"font-size": 12, "font-weight": "bold"}  
}

income_heatmap_config = {
    "innerRadius": 190, 
    "outerRadius": 240, 
    "color": "Purples", 
    #"tooltipContent":{"source": "block_id", "target":"date", "targetEnd":"value"}
}

checkout_heatmap_config = {
    "innerRadius": 110, 
    "outerRadius": 160, 
    "color": "Greys", 
    #"tooltipContent":{"source": "block_id", "target":"date", "targetEnd":"value"}
}

'''holidays_config = {
    "innerRadius": 80,
    "outerRadius": 100,
    "thickness": 4,
    "color": "red",
    "strokeWidth": 0,
    #"tooltipContent": {"source": "block_id", "target": "date", "targetEnd": "holiday"}
}'''

layout = html.Div([
    layout_helpers.insights_subheader,   
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
                                    html.H5("Income", className="text-secondary"),
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

            # Row for data table and settings
            dbc.Row([  

            # Legend for Calendar Circos
            dbc.Row([
                dbc.Col([
                    dbc.Badge("Gross income", pill=True, color="primary"),
                    dbc.Badge("Checkouts", pill=True, color="grey"),
                    dbc.Badge("Public holidays", pill=True, color="danger"),
                    dbc.Badge("Maximum", pill=True, color="success")
                    ], width=1),                 
                ]),
            ])                     
        ], width=6),       

        # Settings menu
        dbc.Offcanvas([

            # common settings for Insights section
            layout_helpers.date_picker_range,
            html.Br(),
            html.Br(),

            html.Hr(),

            # dashboard specific settings
            dcc.Dropdown(
                id="dropdown-city",
                options=branches,
                placeholder="Select city",
                multi=True,
                persistence=True, persistence_type="local"
            ),

            html.Br(),

            dcc.Dropdown(
                id="dropdown-product-line",
                options=product_lines,
                placeholder="Select product line",
                multi=True,
                persistence=True, persistence_type="local"
            )],

            title="Settings",
            placement="end",
            id="settings-menu",
            is_open=False,            
        )          
    ])
])

@callback(
    Output("settings-menu", "is_open"),
    Input("btn-settings", "n_clicks"),
    [State("settings-menu", "is_open")],
)

def toggle_settings_menu(n, is_open):
    if (n):
        return not is_open
    return is_open

@callback([Output("calendar-circos", "layout"),
    Output("calendar-circos", "tracks"),
    Output("kpi-checkouts", "children"),
    Output("kpi-gross-income", "children"),
    Output("kpi-units-sold", "children")],
    [Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    Input("dropdown-city", "value"),
    Input("dropdown-product-line", "value")]
)
def update_dashboard(start_date, end_date, city_dropdown, product_dropdown):

    # filter df by start and end dates selected
    final = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "county")
    final = utils.filter_df_by_dropdown_select(final, product_dropdown, "category_name")
    #final = utils.filter_df_by_dropdown_select(final, payment_dropdown, "Payment")

    # filter df by radio items selections
    #final = utils.filter_df_by_radioitems(final, customer_type, "Customer type")
    #final = utils.filter_df_by_radioitems(final, gender, "Gender")

    # write json file and read it into a variable which will be used for Calendar Circos
    circos_helpers.write_circos_json(final)
    circos_data = circos_helpers.read_json(os.path.join(DATAPATH,"circos_data.json"))   

    # calendar circos returns
    layout = circos_data["calendar"]
    tracks = [
                {
                    "type": "HEATMAP",
                    "data": circos_data["income_histogram"],
                    "config": income_heatmap_config,
                },
                {
                    "type": "HEATMAP",
                    "data": circos_data["sales_histogram"],
                    "config": checkout_heatmap_config,
                },
                {
                    "type": "TEXT",
                    "data": circos_data["text"],
                    "config": text_config
                }
            ]

    # KPI returns
    kpi1 = str(final.shape[0])
    kpi2 = final['sale_dollars'].sum().round(2).astype(str)
    kpi3 = final['bottles_sold'].sum().astype(str)

    # transform df by data table radio items selection
    '''table = final.groupby(by=['date', 'Product line'])[radio_sel_table].sum().round(2).reset_index(name='value')
    transposed = table.pivot(index='date', columns='Product line', values='value').reset_index().rename_axis(None, axis=1)
    transposed['date'] = transposed['date'].dt.date
    transposed.rename(columns={"date": "Date"}, inplace=True)
    transposed['id'] = transposed.index'''

    # data table returns
    '''data=transposed.to_dict('records')
    columns=[{"name": i, "id": i} for i in transposed.columns]
    columns.pop()

    style_data_table_conditional = utils.highlight_max_row(transposed) + [
        {
                'if': {
                    'filter_query': '{{Date}} = {}'.format(i),
                    'column_id': 'Date',
                },
                'backgroundColor': '#FC3939',
                'color': 'white'
            }
            for i in hols
    ]   '''
    
    return layout, tracks, kpi1, kpi2, kpi3
