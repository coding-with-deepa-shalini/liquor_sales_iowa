import dash
from dash import html
import dash_extensions as de
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/',
    title="Iowa Liquor Sales",
    name="Home"
)

options = dict(loop=True, autoplay=True) #rendererSettings=dict(preserveAspectRatio='xMidYmid slice'

layout = html.Div([
    dbc.Row([        
        dbc.Col([
            html.H1("Dash Fall Challenge", className="text-center font-weight-bold", title="Supermarket Sales", style={'font-size':'120px', 'color': 'white'}),
            html.H5([
                "Developed and maintained by - ", 
                html.A("Deepa Shalini Kalakonda",
                href="https://www.linkedin.com/in/deepa-shalini-273385193/", target="_blank", style={'color': 'white'})
            ], style={'color': 'white'})
        ], width=8, className="text-center"),
        dbc.Col([
            de.Lottie(options=options, width="70%", height="70%", url="assets/basket-lottie.json")
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
            ], href="/insights", className="me-5"),
        html.A([
                html.Img(
                    src="assets/eda.png", height="120px"
                ),
            ], className="me-5"),
        html.A([
                html.Img(
                    src="assets/forecast.png", height="120px"
                ),
            ], className="me-5"),
        html.A([
                html.Img(
                    src="assets/help.png", height="120px"
                ),
            ]),
    ], className="d-flex justify-content-center"),
])