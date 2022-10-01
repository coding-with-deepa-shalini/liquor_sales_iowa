import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.PULSE, dbc_css])
server = app.server

sm_bar = dbc.Row(
    [
        dbc.Col([
            html.A(
                html.Img(
                    src=app.get_asset_url('github-logo.png'), height="27px", className="mr-3", 
                ), 
                href="https://github.com/coding-with-deepa-shalini/liquor_sales_iowa", 
                target="_blank"
            )
        ]),
    ],
    className="ms-auto g-3 pe-4",
    align="center",
)

insights_dropdown = dbc.DropdownMenu([ 
    dbc.DropdownMenuItem("Sales Overview", href='/sales-overview'),
    dbc.DropdownMenuItem("Sales by Store", href='/sales-by-store'),
    dbc.DropdownMenuItem("Sales by Liquor type", href='/sales-by-liquor-type')
], label="Insights", className="ms-5")

eda_dropdown = dbc.DropdownMenu([ 
    dbc.DropdownMenuItem("Days of Week", href='/days-of-week'),
    dbc.DropdownMenuItem("Bivariate Trends", href='/bivariate-trends'),
    dbc.DropdownMenuItem("Prices", href='/prices')
], label="Exploratory Analysis", className="ms-2")

forecasting_dropdown = dbc.DropdownMenu([ 
    dbc.DropdownMenuItem("Forecast", href='/forecast'),
    dbc.DropdownMenuItem("Trends", href='/forecast-trends')
], label="Forecasting", className="ms-2")

navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col([
                    html.A(
                        html.Img(
                            src=app.get_asset_url("plotly-dash-logo.png"), height="30px"
                        ),
                        href="https://plot.ly",
                        target="_blank"
                    )
                ]),

                dbc.Col([ 
                    html.A([
                        html.Img(src="assets/home-icon.svg", height="30px"),                        
                    ], href="/")
                ]),

                dbc.Col([ 
                    insights_dropdown
                ]),

                dbc.Col([ 
                    eda_dropdown
                ]),

                dbc.Col([ 
                    forecasting_dropdown
                ])          
            ],
            align="center",
            className="ms-1"
        ),
        dbc.Collapse(sm_bar, id="navbar-collapse", navbar=True)
    ],
    sticky="top",
    color="primary"
)

content = html.Div(dash.page_container)
app.layout = html.Div([dcc.Location(id="url"), navbar, content])

if __name__ == "__main__":
    app.run(debug=False)