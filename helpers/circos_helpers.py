# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
import utils
from . import data_transformation

DATAPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")    

def Decoder(json_obj):
    rv = {}
    for k, v in json_obj.items():
        if isinstance(v, str):
            try:
                rv[k] = float(v)
            except ValueError:
                rv[k] = v
        else:
            rv[k] = v
    return rv

def write_circos_json(df: pd):    
    holidays = pd.read_csv(os.path.join(DATAPATH,"holidays_usa_2020_2021.csv"), index_col=False)

    # sales ring - groupby transformation
    income_ring_df = df.groupby(['year_weeknumber', 'Date'])['sale_dollars'].sum().round(2).reset_index(name='value')
    income_ring_df.set_index('Date', inplace=True)
    # sales ring - fill missing dates (weekends/holidays)
    income_ring_df = income_ring_df.resample('D').first().fillna(0).reset_index()
    income_ring_df['year_weeknumber'] = (income_ring_df['Date']).dt.year.astype(str) + '-' + 'W' + (income_ring_df['Date']).dt.isocalendar().week.astype(str)
    income_ring_df['year_weeknumber'].replace('2021-W53', '2020-W53', inplace=True)

    # bottles sold ring - groupby transformation
    checkout_ring_df = df.groupby(['year_weeknumber', 'Date'])['bottles_sold'].sum().round(2).reset_index(name='value')
    checkout_ring_df.set_index('Date', inplace=True)
    # bottles sold ring - fill missing dates (weekends/holidays)
    checkout_ring_df = checkout_ring_df.resample('D').first().fillna(0).reset_index()
    checkout_ring_df['year_weeknumber'] = (checkout_ring_df['Date']).dt.year.astype(str) + '-' + 'W' + (checkout_ring_df['Date']).dt.isocalendar().week.astype(str)
    checkout_ring_df['year_weeknumber'].replace('2021-W53', '2020-W53', inplace=True)

    text_ring_df = checkout_ring_df[['year_weeknumber', 'Date']].sort_values(by='Date')

    income_ring_df.sort_values(by=['Date'], ignore_index=True, inplace=True)
    checkout_ring_df.sort_values(by=['Date'], ignore_index=True, inplace=True)

    inc = 0
    text_inc = 0.5
    starts = []
    ends = []
    text_positions = []
    no_of_rows = len(checkout_ring_df.index.tolist())

    for idx in checkout_ring_df.index:
        starts.append(inc)
        ends.append(inc+1)
        text_positions.append(text_inc)

        if (idx == no_of_rows-1):
            break

        if (checkout_ring_df['year_weeknumber'].loc[idx] == checkout_ring_df['year_weeknumber'].loc[idx+1]):
            inc += 1
            text_inc += 1
        else:
            inc = 0
            text_inc = 0.5  

    # 1st ring - text - dates
    text_ring_df['position'] = text_positions
    text_ring_df.rename(columns={"year_weeknumber": "block_id", "Date": "value"}, inplace=True)
    text_ring_df = text_ring_df[['block_id', 'position', 'value']]

    # 2nd ring - heatmap - gross income
    income_ring_df.rename(columns={'year_weeknumber': 'block_id'}, inplace=True)
    income_ring_df['start'] = starts
    income_ring_df['end'] = ends

    income_ring_df = income_ring_df[['block_id', 'Date', 'start', 'end', 'value']]
    income_ring_df.sort_values(by=['Date'], inplace=True)

    # 3rd ring - heatmap - checkouts
    checkout_ring_df.rename(columns={'year_weeknumber': 'block_id'}, inplace=True)
    checkout_ring_df['start'] = starts
    checkout_ring_df['end'] = ends

    checkout_ring_df = checkout_ring_df[['block_id', 'Date', 'start', 'end', 'value']]
    checkout_ring_df.sort_values(by=['Date'], inplace=True)

    hols = []
    for i in checkout_ring_df.index:
        for j in holidays.index:
            if (pd.to_datetime(checkout_ring_df['Date'].loc[i], format="%Y-%m-%d") == pd.to_datetime(holidays['Date'].loc[j], format="%Y-%m-%d")):
                hols.append(
                    {
                        'block_id': checkout_ring_df['block_id'].loc[i],
                        'date': checkout_ring_df['Date'].loc[i],
                        'holiday': holidays['holiday'].loc[j],
                        'start': checkout_ring_df['start'].loc[i],
                        'end': checkout_ring_df['end'].loc[i],
                        'color': 'red'
                    }
                )

    holidays_ring_df = pd.DataFrame(hols)

    # base layout
    calendar = checkout_ring_df.value_counts(['block_id'], sort=False).reset_index(name='len')   
    calendar.sort_values(by=['block_id'], key=lambda s: s.str[6:].astype(int), inplace=True)
    calendar.sort_values(by=['block_id'], inplace=True)

    calendar['label'] = calendar['block_id']
    calendar['color'] = "#ffffff"
    calendar.rename(columns={'block_id': 'id'}, inplace=True)
    calendar = calendar[['id', 'label', 'color', 'len']]

    # convert dataframe to json
    text_ring_json = utils.write_readable_json(text_ring_df)
    income_ring_json = utils.write_readable_json(income_ring_df)
    checkout_ring_json = utils.write_readable_json(checkout_ring_df)
    holidays_ring_json = utils.write_readable_json(holidays_ring_df)

    calendar_json = json.loads(calendar.astype(str).to_json(orient='records'))

    # json objects which will be in the final file
    checkouts_json_str = json.dumps(checkout_ring_json).replace('[', '{"sales_histogram": [') + ', '
    income_json_str = json.dumps(income_ring_json).replace('[', '"income_histogram": [') + ', '
    text_json_str = json.dumps(text_ring_json).replace('[', '"text": [') + ', '
    holidays_json_str = json.dumps(holidays_ring_json).replace('[', '"holidays": [') + ', '
    calendar_json_str = json.dumps(calendar_json).replace('[', '"calendar": [') + '}'

    final_json = checkouts_json_str + income_json_str + text_json_str + holidays_json_str + calendar_json_str

    with open(os.path.join(DATAPATH,"circos_data.json"), 'w') as file:
        file.write(json.dumps(json.loads(final_json, object_hook=Decoder), indent = 4, ensure_ascii = False))

def read_json(file_json: str) -> dict():
    with open(file_json) as file:
        data = json.load(file)

    return data

