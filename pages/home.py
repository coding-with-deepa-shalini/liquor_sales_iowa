import dash
from dash import html
import dash_extensions as de
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/',
    title="Iowa Liquor Sales",
    name="Home",
    image="metatag-image.png",
    description="Dash app developed for the Dash Autumn Challenge. The Iowa liquor sales data was used."
)

options = dict(loop=True, autoplay=True) #rendererSettings=dict(preserveAspectRatio='xMidYmid slice'
tooltip_placement = "bottom"

layout = html.Div([
    dbc.Row([      
        dbc.Col([
            html.H1("Dash Autumn Challenge", className="text-center font-weight-bold", title="Iowa Liquor Sales", style={'font-size':'110px', 'color': 'white'}),
            html.H5([
                "Developed and maintained by - ", 
                html.A("Deepa Shalini Kalakonda",
                href="https://www.linkedin.com/in/deepa-shalini-273385193/", target="_blank", style={'color': 'white'})
            ], style={'color': 'white'})
        ], width=8, className="text-center ms-1"),
        dbc.Col([
            de.Lottie(options=options, width="70%", height="90%", url="assets/wine-glass-lottie.json")
        ], width=4)
    ], justify="center", align="center", className="g-0 bg-primary"),

    html.Br(),
    html.Br(),
    html.Br(),

    html.Div([
        html.A([
                html.Img(
                    src="assets/insights.png", height="120px"                   
                ),
            ], href="/insights", className="me-5", id="insights-link-home"),
        html.A([
                html.Img(
                    src="assets/eda.png", height="120px"
                ),
            ], href="/exploratory-analysis", className="me-5", id="eda-link-home"),
        html.A([
                html.Img(
                    src="assets/forecast.png", height="120px"
                ),
            ], href="/forecasting", className="me-5", id="forecasting-link-home"),
        html.A([
                html.Img(
                    src="assets/help.png", height="120px"
                ),
            ], href="/summary", id="help-link-home"),
    ], className="d-flex justify-content-center"),

    dbc.Tooltip("Insights", target="insights-link-home", placement=tooltip_placement),
    dbc.Tooltip("Exploratory Analysis", target="eda-link-home", placement=tooltip_placement),
    dbc.Tooltip("Forecasting", target="forecasting-link-home", placement=tooltip_placement),
    dbc.Tooltip("Summary", target="help-link-home", placement=tooltip_placement)
])