import json
import pandas as pd

def write_readable_json(df: pd) -> list():
    return json.loads(df.astype(str).to_json(orient='records', date_format="iso")) 

def get_unique_values(df: pd, column_name: str) -> pd:
    return df[column_name].unique().tolist()

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
