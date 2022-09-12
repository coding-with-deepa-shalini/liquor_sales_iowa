import pandas as pd
import datetime

def transform_sales_data_overview(df):
    df['Date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')

    df['weekday'] = (df['Date']).dt.day_name()
    df['day'] = (df['Date']).dt.day
    df['month'] = (df['Date']).dt.month
    df['year'] = (df['Date']).dt.year
    df['month_year'] = df['month'].astype(str) + '-' + df['year'].astype(str)
    df['year_month'] = df['year'].astype(str) + '-' + df['month'].astype(str)
    df['year_weeknumber'] = df['year'].astype(str) + '-' + 'W' + (df['Date']).dt.isocalendar().week.astype(str)
    df['week_start_date'] = [datetime.datetime.strptime(x + '-1', '%G-W%V-%u') for x in df['year_weeknumber'].tolist()]
    df['county'] = df['county'].str.capitalize()

    df.sort_values(['Date'], inplace=True)

    return df

def transform_sales_data_by_store(df):
    transformed = transform_sales_data_overview(df)

    transformed.loc[transformed['store_location'] == 'POINT (-95.79728 45.009612)', 'store_location'] = 'POINT (-91.11346 40.80724)'
    transformed.loc[transformed['store_location'] == 'POINT (-73.982421 40.305231000000006)', 'store_location'] = 'POINT (-94.44483 42.95923)'
    transformed['lat'] = transformed['store_location'].str.split(' ').str.get(2).str.replace(')', '').astype(float)
    transformed['lon'] = transformed['store_location'].str.split(' ').str.get(1).str.replace('(', '').astype(float)

    return transformed