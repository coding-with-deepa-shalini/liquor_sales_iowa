import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/summary',
    title="Iowa Liquor Sales",
    name="Summary"
)

layout = dbc.Container(
    dbc.Row([ 
        dbc.Col([ 
            html.Br(), html.Br(),
            html.H3("App Summary"),
            html.Hr(),

            dcc.Markdown('''
            The dataset used for this application has 50,000 rows. It contains liquor sales in Iowa from December, 2020 till November 2021. 
            
            A new column called 'liquor_type' was added to the dataset to group the categories of liquor which is more user-friendly than the categories provided in the dataset.

            The app consists of three sections - 'Insights', 'Exploratory Analysis' and 'Forecasting'. 'Insights' and 'Exploratory Analysis' contains data visualizations which provide powerful data-driven insights which can help the liquor companies with their manufacturing and distribution operations.

            The 'Forecasting' section provides a forecast of the future sales of liquor in the state of Iowa, the user the given the freedom to play around with certain parameters to tune the model and to generate a relevant forecasting model. The **Prophet library from Meta** is being used to generate the forecast and the trends.
            '''),

            html.Br(),

            html.H3("Improvements"),

            html.Hr(),

            dcc.Markdown('''
            The app can be improved in many ways to provide better data-driven insights and forecast to help the liquor industry. 

            * The 'Insights' section can have a choropleth map with the amount of liquor sold to Iowa by ocunty.

            * The 'Exploratiory Analysis' section can have a page dedicated to clustering or anomaly detection.

            * The 'Forecasting' section can have better forecasts generated by using more data. The forecast will be better if 3-4 years worth of liquor sales data is being used.

            * The forecasts generated will also be better by adding more regressors and more parameters provided in the **Prophet** library.
            ''')
        ])
    ])
)