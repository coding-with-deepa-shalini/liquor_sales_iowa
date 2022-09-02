import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/insights',
    title="Supermarket Sales",
    name="Insights"
)

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
                ], href="/sales-overview", className="me-3"),
            html.A([
                    html.Img(
                        src="assets/income-by-product.png", height="120px"
                    ),
                ], href="/income-by-product-line", className="me-3"),
            html.A([
                    html.Img(
                        src="assets/income-by-branch.png", height="120px"
                    ),
                ]),
        ], className="d-flex justify-content-center m-3 bg-warning")
    ], placement="bottom", close_button=False, is_open=True, backdrop=False, className="bg-warning", style={'height': '50%'}),    
])