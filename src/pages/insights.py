from json import tool
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/insights',
    title="Iowa Liquor Sales",
    name="Insights"
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
        html.H1("Insights", className="text-center font-weight-bold", style={'font-size':'120px'})
    ], className="d-flex align-content-end flex-wrap justify-content-center"),      

    dbc.Offcanvas([
        html.Div([
            html.A([
                    html.Img(
                        src="assets/income-overview.png", height="120px"                   
                    ),
                ], href="/sales-overview", className="me-3", id="insights-overview"),
            html.A([
                    html.Img(
                        src="assets/income-by-branch.png", height="120px"
                    ),
                ], href="/sales-by-store", className="me-3", id="insights-by-store"),
            html.A([
                    html.Img(
                        src="assets/income-by-product.png", height="120px"
                    ),
                ], href="/sales-by-liquor-type", id="insights-by-type"),
        ], className="d-flex justify-content-center m-3 bg-warning")
    ], placement="bottom", close_button=False, is_open=True, backdrop=False, className="bg-warning", style={'height': '50%'}),    

    dbc.Tooltip("Sales Overview", target="insights-overview", placement=tooltip_placement),
    dbc.Tooltip("Sales by Store", target="insights-by-store", placement=tooltip_placement),
    dbc.Tooltip("Sales by Liquor type", target="insights-by-type", placement=tooltip_placement)
])