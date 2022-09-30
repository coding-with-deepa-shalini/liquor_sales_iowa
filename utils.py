import json
import pandas as pd
from math import log, floor

def format_large_numbers(number):
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])

def write_readable_json(df: pd) -> list():
    return json.loads(df.astype(str).to_json(orient='records', date_format="iso")) 

def get_unique_values(df: pd, column_name: str) -> pd:
    categories = df[column_name].unique().tolist()
    categories_without_nans = [x for x in categories if str(x) != 'nan']
    return sorted(categories_without_nans)

def filter_df_by_dropdown_select(df: pd, dropdown_id: list(), column_name: str) -> pd:
    if (dropdown_id != None):
        if (len(dropdown_id) > 0):
            final = df[df[column_name].isin(dropdown_id)]
            return final

        else:
            return df
            
    else:
        return df

def filter_df_by_radioitems(df: pd, selection: str, column_name: str) -> pd:
    if (selection != None or selection != ""):
        if (selection == "Both"):
            return df 
        
        else:
            final = df[df[column_name] == selection]
            return final 
    
    else:
        return df

def highlight_max_row(df: pd) -> list():
    df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
    return [
        {
            'if': {
                'filter_query': '{{id}} = {}'.format(i),
                'column_id': col
            },
            'backgroundColor': '#13B955',
            'color': 'white'
        }
        # idxmax(axis=1) finds the max indices of each row
        for (i, col) in enumerate(
            df_numeric_columns.idxmax(axis=1)
        )
    ]

def data_bars(df, column, background_colour):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [
        ((df[column].max() - df[column].min()) * i) + df[column].min()
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    {background_colour} 0%,
                    {background_colour} {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(background_colour=background_colour, max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles
