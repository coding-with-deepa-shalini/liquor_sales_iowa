import pandas as pd
import datetime

def transform_sales_data(df):
    df['Date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')

    df['weekday'] = (df['Date']).dt.day_name()
    #df['weeknumber'] = 'week' + (df['Date']).dt.isocalendar().week.astype(str)
    df['day'] = (df['Date']).dt.day
    df['month'] = (df['Date']).dt.month
    df['year'] = (df['Date']).dt.year
    df['month_year'] = df['month'].astype(str) + '-' + df['year'].astype(str)
    #df['weeknumber_year'] = df['weeknumber'].astype(str) + '-' + df['year'].astype(str)
    df['year_weeknumber'] = df['year'].astype(str) + '-' + 'W' + (df['Date']).dt.isocalendar().week.astype(str)
    df['week_start_date'] = [datetime.datetime.strptime(x + '-1', '%G-W%V-%u') for x in df['year_weeknumber'].tolist()]
    df.sort_values(['Date'], inplace=True)

    return df