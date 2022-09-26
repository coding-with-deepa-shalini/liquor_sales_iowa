import os
import dash
import pandas as pd
from fbprophet import Prophet
import dash_bootstrap_components as dbc
from fbprophet.plot import plot_components_plotly
from dash import dcc, html, Input, Output, callback
from dash_bootstrap_templates import load_figure_template
from fbprophet.diagnostics import cross_validation, performance_metrics

import utils
from helpers import layout_helpers, data_transformation

dash.register_page(
    __name__,
    path='/trends',
    title="Iowa Liquor Sales",
    name="Trends"
)

load_figure_template("pulse")

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

raw_df = pd.read_csv(os.path.join(DATAPATH,"Iowa_liquor_sales_2021_minimal_with_type.csv"), index_col=False)
df = data_transformation.transform_sales_data_overview(raw_df)

forecast_text = {'bottles_sold': 'Bottles sold', 'volume_sold_liters': 'Volume sold (in litres)'}

layout = html.Div([ 
    layout_helpers.forecasting_get_subheader(),

    html.Br(),

    dbc.Row([
        dbc.Col([ 
            layout_helpers.model_parameters_card,            
            layout_helpers.filter_training_set_card
        ], width=2, className="ms-4 dbc"),

        dbc.Col([ 
            dbc.Spinner(children=[dcc.Graph(id='prophet-output-components')], color='primary'),
        ], width=7, className="ms-5"),

        dbc.Col([ 
            html.Br(),
            html.Br(),
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(children=[html.H1({}, id='kpi1-trends', className='card-title')], type='dot'),
                ]),
                dbc.CardFooter("MAPE")
            ], color="secondary", outline=True, style={'width': '70%'}),
            html.Br(),
            html.Br(), 
            html.Br(),
            html.Br(), 
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(children=[html.H1({}, id='kpi2-trends', className='card-title')], type='dot'),
                ]),
                dbc.CardFooter("RMSE")
            ], color="secondary", outline=True, style={'width': '70%'}),
            html.Br(),
            html.Br(), 
            html.Br(),
            html.Br(), 
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(children=[html.H1({}, id='kpi3-trends', className='card-title')], type='dot'),
                ]),
                dbc.CardFooter("Normalized RMSE")
            ], color="secondary", outline=True, style={'width': '70%'})
        ], className="ms-5 me-5")              
    ])
])

@callback([Output("kpi1-trends", "children"),
    Output("kpi2-trends", "children"),
    Output("kpi3-trends", "children"),
    Output("prophet-output-components", "figure")],
    [Input("radio-items-var-forecast", "value"),
    Input("number-of-months-to-predict", "value"),
    Input("confidence-interval-slider", "value"),
    Input("weekly-seasonality-switch", "value"),
    Input("monthly-seasonality-switch", "value"),
    Input("yearly-seasonality-switch", "value"),
    Input("holidays-switch", "value"),
    Input("dropdown-type-name-forecasting", "value"),
    Input("dropdown-vendor-name-forecasting", "value")]
)
def update_dashboard(var_to_forecast, num_months_to_predict, conf_interval, weekly_seasonality, monthly_seasonality, yearly_seasonality, holidays, type_dropdown, vendor_dropdown):

    final = df
    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, type_dropdown, "liquor_type")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")

    final_df = final.groupby('Date')[var_to_forecast].sum().reset_index()
    final_df.rename(columns={'Date': 'ds', var_to_forecast: 'y'}, inplace=True)

    confidence_interval = conf_interval / 100
    model = Prophet(interval_width=confidence_interval, weekly_seasonality=weekly_seasonality, yearly_seasonality=yearly_seasonality, changepoint_prior_scale=0.1)

    if (monthly_seasonality):
        model.add_seasonality(name='monthly', period=30.5, fourier_order=1)

    if (holidays):
        model.add_country_holidays(country_name='US')

    model.fit(final_df)

    periods_to_predict = int(round(num_months_to_predict * 30.5))
    future = model.make_future_dataframe(periods=periods_to_predict, freq='D')
    forecast = model.predict(future)

    df_cv = cross_validation(model, initial='330 days', period='15 days', horizon = '30 days')
    df_p = performance_metrics(df_cv)

    max_rmse = max(final[var_to_forecast].tolist())
    min_rmse = min(final[var_to_forecast].tolist())

    mape = round(df_p['mape'].tolist()[-1], 2)
    rmse = round(df_p['rmse'].tolist()[-1], 2)
    norm_rmse = round(rmse / (max_rmse - min_rmse), 2)

    fig = plot_components_plotly(model, forecast)
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
        title=forecast_text[var_to_forecast] + " - Trends",
        height=750, width=1100,
        template="pulse"
    )

    return str(mape) + '%', rmse, norm_rmse, fig