import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/forecasting',
    title="Iowa Liquor Sales",
    name="Forecasting"
)

tooltip_placement = "bottom"

layout = html.Div([
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    html.Div([ 
        html.H1("Forecasting", className="text-center font-weight-bold", style={'font-size':'120px'})
    ], className="d-flex align-content-end flex-wrap justify-content-center"),      

    dbc.Offcanvas([
        html.Div([
            html.A([
                    html.Img(
                        src="assets/forecasting-forecast.png", height="120px"                   
                    ),
                ], href="/forecast", className="me-3", id="forecasting-forecast"),
            html.A([
                    html.Img(
                        src="assets/forecasting-trends.png", height="120px"
                    ),
                ], href="/forecast-trends", className="me-3", id="forecasting-trends"),
        ], className="d-flex justify-content-center m-3 bg-success")
    ], placement="bottom", close_button=False, is_open=True, backdrop=False, className="bg-success", style={'height': '50%'}),    

    dbc.Tooltip("Forecast", target="forecasting-forecast", placement=tooltip_placement),
    dbc.Tooltip("Trends", target="forecasting-trends", placement=tooltip_placement)
])