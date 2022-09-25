import os
import dash
import pandas as pd
from fbprophet import Prophet
import plotly.graph_objects as go
from fbprophet.plot import plot_plotly
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
from dash_bootstrap_templates import load_figure_template
from fbprophet.diagnostics import cross_validation, performance_metrics

import utils
from helpers import layout_helpers, data_transformation

dash.register_page(
    __name__,
    path='/forecast',
    title="Iowa Liquor Sales",
    name="Forecast"
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
            dbc.Spinner(children=[dcc.Graph(id='prophet-output-graph')], color='primary'),
            dbc.Spinner(children=[dcc.Graph(id='go-figure-predicted-graph')], color='primary')
        ], width=7, className="ms-3"),

        dbc.Col([ 
            html.Br(),
            html.Br(),
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(children=[html.H1({}, id='kpi1-forecast', className='card-title')], type='dot', color='#E0E0EB'),
                ]),
                dbc.CardFooter("MAPE")
            ], color="secondary", outline=True),
            html.Br(),
            html.Br(), 
            html.Br(),
            html.Br(), 
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(children=[html.H1({}, id='kpi2-forecast', className='card-title')], type='dot'),
                ]),
                dbc.CardFooter("RMSE")
            ], color="secondary", outline=True),
            html.Br(),
            html.Br(), 
            html.Br(),
            html.Br(), 
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(children=[html.H1({}, id='kpi3-forecast', className='card-title')], type='dot'),
                ]),
                dbc.CardFooter("Normalized RMSE")
            ], color="secondary", outline=True)
        ], width=2, className="ms-5 me-5")      
    ])
])

@callback([Output("kpi1-forecast", "children"),
    Output("kpi2-forecast", "children"),
    Output("kpi3-forecast", "children"),
    Output("prophet-output-graph", "figure"),
    Output("go-figure-predicted-graph", "figure")],
    [Input("radio-items-var-forecast", "value"),
    Input("number-of-months-to-predict", "value"),
    Input("confidence-interval-slider", "value"),
    Input("weekly-seasonality-switch", "value"),
    Input("monthly-seasonality-switch", "value"),
    Input("yearly-seasonality-switch", "value"),
    Input("holidays-switch", "value"),
    Input("dropdown-type-name-forecasting", "value"),
    Input("dropdown-vendor-name-forecasting", "value"),
    Input("dropdown-city-name-forecasting", "value"),
    Input("dropdown-county-name-forecasting", "value")]
)
def update_dashboard(var_to_forecast, num_months_to_predict, conf_interval, weekly_seasonality, monthly_seasonality, yearly_seasonality, holidays, type_dropdown, vendor_dropdown, city_dropdown, county_dropdown):

    final = df
    # filter df by dropdown selections
    final = utils.filter_df_by_dropdown_select(final, type_dropdown, "liquor_type")
    final = utils.filter_df_by_dropdown_select(final, vendor_dropdown, "vendor_name")
    final = utils.filter_df_by_dropdown_select(final, city_dropdown, "city")
    final = utils.filter_df_by_dropdown_select(final, county_dropdown, "county")

    final = final.groupby('Date')[var_to_forecast].sum().reset_index()
    final.rename(columns={'Date': 'ds', var_to_forecast: 'y'}, inplace=True)

    confidence_interval = conf_interval / 100
    model = Prophet(interval_width=confidence_interval, weekly_seasonality=weekly_seasonality, yearly_seasonality=yearly_seasonality, changepoint_prior_scale=0.1)

    if (monthly_seasonality):
        model.add_seasonality(name='monthly', period=30.5, fourier_order=1)

    if (holidays):
        model.add_country_holidays(country_name='US')

    model.fit(final)

    periods_to_predict = int(round(num_months_to_predict * 30.5))
    future = model.make_future_dataframe(periods=periods_to_predict, freq='D')
    forecast = model.predict(future)

    df_cv = cross_validation(model, initial='330 days', period='15 days', horizon = '30 days')
    df_p = performance_metrics(df_cv)

    max_rmse = max(df_p['rmse'].tolist())
    min_rmse = min(df_p['rmse'].tolist())

    mape = round(df_p['mape'].tolist()[-1], 2)
    rmse = round(df_p['rmse'].tolist()[-1], 2)
    norm_rmse = round(rmse / (max_rmse - min_rmse), 2)

    fig1 = plot_plotly(model, forecast)
    fig1.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
                    xaxis_title='Date', yaxis_title=forecast_text[var_to_forecast], 
                    height=400, width=1100, 
                    title=forecast_text[var_to_forecast] + " - Daily Forecast",
                    template="pulse"
    )

    future_fig2 = model.make_future_dataframe(periods=num_months_to_predict, freq='M')
    forecast_fig2 = model.predict(future_fig2)
    
    to_plot = pd.merge(final, forecast_fig2, on='ds', how='outer')
    to_plot['type'] = 'Observed'
    to_plot.loc[pd.isna(to_plot['y']), 'type'] = 'Predicted'

    observed = to_plot[to_plot['type'] == 'Observed']
    predicted = to_plot[to_plot['type'] == 'Predicted']

    fig2 = go.Figure()

    predicted_x = list(predicted['ds'])
    y_upper = list(predicted['yhat_upper'])
    y_lower = list(predicted['yhat_lower'])

    fig2.add_trace(go.Scatter(x=observed['ds'], y=observed['y'], mode='lines', name='Observed'))

    fig2.add_trace(go.Scatter(x=predicted['ds'], y=predicted['yhat'], mode='lines+markers', 
                            name='Predicted'
                            ))

    fig2.add_trace(go.Scatter(x=predicted_x+predicted_x[::-1], y=y_upper+y_lower[::-1], 
                            fill='toself', fillcolor='rgba(239,85,59,0.3)', 
                            name='Uncertainty',
                            line=dict(color='rgba(255,255,255,0)')
                            ))

    fig2.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)'},
                    xaxis_title='Date', yaxis_title=forecast_text[var_to_forecast],
                    xaxis=dict(rangeslider=dict(autorange=True)),
                    height=350,
                    title=forecast_text[var_to_forecast] + " - Monthly Forecast",
                    template="pulse")

    return str(mape) + '%', rmse, norm_rmse, fig1, fig2

