import pandas as pd
from dstapi import DstApi

def load_IFOR41(ULLIG, KOMMUNEDK, TID):
    """ loads and cleans Gini coefficient data from the IFOR41 table
    
    Args:
        ULLIG (str): indicator for the inequality metric to query
        KOMMUNEDK (str): indicator for the municipalities to query
        TID (str): indicator for the time periods to query
        
    Returns:
        df (pandas.DataFrame): cleaned dataframe containing Gini coefficients
    """
    params = {
        'table': 'IFOR41', 'format': 'BULK', 'lang': 'en',
        'variables': [
            {'code': 'ULLIG', 'values': [ULLIG]},
            {'code': 'KOMMUNEDK', 'values': [KOMMUNEDK]},
            {'code': 'TID', 'values': [TID]}
        ]
    }    
    df = DstApi('IFOR41').get_data(params=params)
    df['INDHOLD'] = df['INDHOLD'].astype(float)
    df = df.rename(columns={'INDHOLD': 'gini', 'TID': 'year'})
    df = df.drop(columns=['ULLIG'])
    df = df.sort_values(by=['KOMMUNEDK', 'year']).reset_index(drop=True)
    return df

def load_IFOR32(DECILGEN, KOMMUNEDK, TID):
    """ loads data from IFOR32 and calculates the top 10 percent income share
         
     Args:
        DECILGEN (str): indicator for the income deciles to query
        KOMMUNEDK (str): indicator for the municipalities to query
        TID (str): indicator for the time periods to query
             
    Returns:
        df_final (pandas.DataFrame): dataframe with top 10 percent share by municipality and year
    """
    params = {
        'table': 'IFOR32', 'format': 'BULK', 'lang': 'en',
        'variables': [
            {'code': 'DECILGEN', 'values': [DECILGEN]},
            {'code': 'KOMMUNEDK', 'values': [KOMMUNEDK]},
            {'code': 'TID', 'values': [TID]}
        ]
    }    
    df = DstApi('IFOR32').get_data(params=params)
    df['INDHOLD'] = df['INDHOLD'].astype(float)
    
    df_pivot = df.pivot(index=['KOMMUNEDK', 'TID'], columns='DECILGEN', values='INDHOLD')
    df_pivot['top_10_share'] = df_pivot['Tenth decil'] / df_pivot.sum(axis=1)
    
    df_final = df_pivot[['top_10_share']].reset_index()
    df_final = df_final.rename(columns={'TID': 'year'})
    df_final = df_final.sort_values(by=['KOMMUNEDK', 'year']).reset_index(drop=True)
    df_final.columns.name = None
    return df_final