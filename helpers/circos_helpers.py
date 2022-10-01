# -*- coding: utf-8 -*-
import os
import json
import utils
import pandas as pd

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
    dollars_ring_df = df.groupby(['year_month', 'Date'])['sale_dollars'].sum().round(2).reset_index(name='value')
    dollars_ring_df.set_index('Date', inplace=True)
    # sales ring - fill missing dates (weekends/holidays)
    dollars_ring_df = dollars_ring_df.resample('D').first().fillna(0).reset_index()
    dollars_ring_df['year_month'] = (dollars_ring_df['Date']).dt.year.astype(str) + '-' + (dollars_ring_df['Date']).dt.month.astype(str)

    # volume sold litres ring - groupby transformation
    volume_ring_df = df.groupby(['year_month', 'Date'])['sale_dollars'].sum().round(2).reset_index(name='value')
    volume_ring_df.set_index('Date', inplace=True)
    # volume sold litres ring - fill missing dates (weekends/holidays)
    volume_ring_df = volume_ring_df.resample('D').first().fillna(0).reset_index()
    volume_ring_df['year_month'] = (volume_ring_df['Date']).dt.year.astype(str) + '-' + (volume_ring_df['Date']).dt.month.astype(str)

    # bottles sold ring - groupby transformation
    bottles_ring_df = df.groupby(['year_month', 'Date'])['bottles_sold'].sum().round(2).reset_index(name='value')
    bottles_ring_df.set_index('Date', inplace=True)
    # bottles sold ring - fill missing dates (weekends/holidays)
    bottles_ring_df = bottles_ring_df.resample('D').first().fillna(0).reset_index()
    bottles_ring_df['year_month'] = (bottles_ring_df['Date']).dt.year.astype(str) + '-' + (bottles_ring_df['Date']).dt.month.astype(str)

    text_ring_df = bottles_ring_df[['year_month', 'Date']].sort_values(by='Date')

    dollars_ring_df.sort_values(by=['Date'], ignore_index=True, inplace=True)
    volume_ring_df.sort_values(by=['Date'], ignore_index=True, inplace=True)
    bottles_ring_df.sort_values(by=['Date'], ignore_index=True, inplace=True)

    inc = 0
    text_inc = 0.5
    starts = []
    ends = []
    text_positions = []
    no_of_rows = len(bottles_ring_df.index.tolist())

    for idx in bottles_ring_df.index:
        starts.append(inc)
        ends.append(inc+1)
        text_positions.append(text_inc)

        if (idx == no_of_rows-1):
            break

        if (bottles_ring_df['year_month'].loc[idx] == bottles_ring_df['year_month'].loc[idx+1]):
            inc += 1
            text_inc += 1
        else:
            inc = 0
            text_inc = 0.5  

    # 1st ring - text - dates
    text_ring_df['position'] = text_positions
    text_ring_df.rename(columns={"year_month": "block_id", "Date": "value"}, inplace=True)
    text_ring_df = text_ring_df[['block_id', 'position', 'value']]

    # 2nd ring - heatmap - sale dollars
    dollars_ring_df.rename(columns={'year_month': 'block_id'}, inplace=True)
    dollars_ring_df['start'] = starts
    dollars_ring_df['end'] = ends

    dollars_ring_df = dollars_ring_df[['block_id', 'Date', 'start', 'end', 'value']]
    dollars_ring_df.sort_values(by=['Date'], inplace=True)

    # 3rd ring - heatmap - volume sold litres
    volume_ring_df.rename(columns={'year_month': 'block_id'}, inplace=True)
    volume_ring_df['start'] = starts
    volume_ring_df['end'] = ends

    volume_ring_df = volume_ring_df[['block_id', 'Date', 'start', 'end', 'value']]
    volume_ring_df.sort_values(by=['Date'], inplace=True)

    # 3rd ring - heatmap - bottles sold
    bottles_ring_df.rename(columns={'year_month': 'block_id'}, inplace=True)
    bottles_ring_df['start'] = starts
    bottles_ring_df['end'] = ends

    bottles_ring_df = bottles_ring_df[['block_id', 'Date', 'start', 'end', 'value']]
    bottles_ring_df.sort_values(by=['Date'], inplace=True)

    hols = []
    for i in bottles_ring_df.index:
        for j in holidays.index:
            if (pd.to_datetime(bottles_ring_df['Date'].loc[i], format="%Y-%m-%d") == pd.to_datetime(holidays['Date'].loc[j], format="%Y-%m-%d")):
                hols.append(
                    {
                        'block_id': bottles_ring_df['block_id'].loc[i],
                        'date': bottles_ring_df['Date'].loc[i],
                        'holiday': holidays['holiday'].loc[j],
                        'start': bottles_ring_df['start'].loc[i],
                        'end': bottles_ring_df['end'].loc[i],
                        'color': 'red'
                    }
                )

    holidays_ring_df = pd.DataFrame(hols)

    # base layout
    calendar = bottles_ring_df.value_counts(['block_id'], sort=False).reset_index(name='len')
    calendar.sort_values(by=['block_id'], inplace=True)

    calendar['label'] = calendar['block_id']
    calendar['color'] = "#ffffff"
    calendar.rename(columns={'block_id': 'id'}, inplace=True)
    calendar = calendar[['id', 'label', 'color', 'len']]

    # convert dataframe to json
    text_ring_json = utils.write_readable_json(text_ring_df)
    dollars_ring_json = utils.write_readable_json(dollars_ring_df)
    volume_ring_json = utils.write_readable_json(volume_ring_df)
    bottles_ring_json = utils.write_readable_json(bottles_ring_df)
    holidays_ring_json = utils.write_readable_json(holidays_ring_df)

    calendar_json = json.loads(calendar.astype(str).to_json(orient='records'))

    # json objects which will be in the final file
    bottles_json_str = json.dumps(bottles_ring_json).replace('[', '{"sales_histogram": [') + ', '
    dollars_json_str = json.dumps(dollars_ring_json).replace('[', '"income_histogram": [') + ', '
    volume_json_str = json.dumps(volume_ring_json).replace('[', '"volume_histogram": [') + ', '
    text_json_str = json.dumps(text_ring_json).replace('[', '"text": [') + ', '
    holidays_json_str = json.dumps(holidays_ring_json).replace('[', '"holidays": [') + ', '
    calendar_json_str = json.dumps(calendar_json).replace('[', '"calendar": [') + '}'

    final_json = bottles_json_str + dollars_json_str + volume_json_str + text_json_str + holidays_json_str + calendar_json_str

    with open(os.path.join(DATAPATH,"circos_data.json"), 'w') as file:
        file.write(json.dumps(json.loads(final_json, object_hook=Decoder), indent = 4, ensure_ascii = False))

def read_json(file_json: str) -> dict():
    with open(file_json) as file:
        data = json.load(file)

    return data

