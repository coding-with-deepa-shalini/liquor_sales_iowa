import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.PULSE])
server = app.server

sm_bar = dbc.Row(
    [
        dbc.Col([
            html.A(
                html.Img(
                    src=app.get_asset_url('github-logo.png'), height="27px", className="mr-3", 
                ), 
                href="https://www.github.com/", 
                target="_blank"
            )
        ]),
    ],
    className="ms-auto g-3 pe-4",
    align="center",
)

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