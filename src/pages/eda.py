import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/exploratory-analysis',
    title="Iowa Liquor Sales",
    name="Exploratory Analysis"
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
        html.H1("Exploratory Analysis", className="text-center font-weight-bold", style={'font-size':'120px'})
    ], className="d-flex align-content-end flex-wrap justify-content-center"),      

    dbc.Offcanvas([
        html.Div([
            html.A([
                    html.Img(
                        src="assets/eda-days-of-week.png", height="120px"                   
                    ),
                ], href="/days-of-week", className="me-3", id="eda-days-of-week"),
            html.A([
                    html.Img(
                        src="assets/eda-bivariate.png", height="120px"
                    ),
                ], href="/bivariate-trends", className="me-3", id="eda-bivariate-trends"),
            html.A([
                    html.Img(
                        src="assets/eda-prices.png", height="120px"
                    ),
                ], href="/prices", className="me-3", id="eda-prices")
        ], className="d-flex justify-content-center m-3 bg-secondary")
    ], placement="bottom", close_button=False, is_open=True, backdrop=False, className="bg-secondary", style={'height': '50%'}),    

    dbc.Tooltip("Days of Week", target="eda-days-of-week", placement=tooltip_placement),
    dbc.Tooltip("Bivariate Trends", target="eda-bivariate-trends", placement=tooltip_placement),
    dbc.Tooltip("Prices", target="eda-prices", placement=tooltip_placement)
])