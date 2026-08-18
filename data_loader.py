import pandas as pd
from dstapi import DstApi


# a. Setting up a function to load the gini coefficient for all of denmark
def load_IFOR41(ULLIG,KOMMUNEDK,TID,varname):
    """ Downloads and cleans Gini coefficient data from Statistics Denmark.
    
    Args:
        ULLIG (str): Variable code for inequality.
        KOMMUNEDK (str): Municipality code.
        TID (str): Time variable.
        varname (str): Unused variable name.
        
    Returns:
        df (pd.DataFrame): Cleaned dataframe with Gini coefficients indexed by year.
    """

    # b. setting up the parameters
    params = {
        'table': 'IFOR41',
        'format': 'BULK', 
        'lang': 'en',
        'variables': [
            {'code': 'ULLIG', 'values': ['70']},
            {'code': 'KOMMUNEDK', 'values': ['000']},
            {'code': 'TID', 'values': ['*']},
            ]
    }    

    # c. downloading data from Statistics Denmark
    df = DstApi('IFOR41').get_data(params=params)

    # d. setting types and renaming columns
    df['INDHOLD'] = df['INDHOLD'].astype(float)
    df = df.drop(columns=['ULLIG'])
    df = df.rename(columns={'INDHOLD': 'Gini Coefficient', 'TID': 'year'})
    df = df.set_index('year').sort_index()
    
    return df


# a. Setting up a function to load the top 10-pct. income share
def load_IFOR32(DECILGEN, KOMMUNEDK, Tid, varname):

    """ Downloads and formats income decile data from Statistics Denmark.
    
    Args:
        DECILGEN (str): Decile variable code.
        KOMMUNEDK (str): Municipality code.
        Tid (str): Time variable.
        varname (str): Unused variable name.
        
    Returns:
        df_final (pd.DataFrame): DataFrame containing the top 10% income share.
    """

    params = {
        'table': 'IFOR32',
        'format': 'BULK', 
        'lang': 'en',
        'variables': [
            {'code': 'DECILGEN', 'values': ['*']},
            {'code': 'KOMMUNEDK', 'values': ['000']},
            {'code': 'TID', 'values': ['*']},
            ]
    }    

    # c. downloading data from Statistics Denmark
    df = DstApi('IFOR32').get_data(params=params)

    # d. Adjusting the type to a float for the income decile variable
    df['INDHOLD'] = df['INDHOLD'].astype(float)
    df_pivot = df.pivot(index='TID', columns='DECILGEN', values='INDHOLD')

    # e. Calculating the share of income for the top 10% of the wealth distribution in Denmark
    df_pivot['top_10_share'] = df_pivot['Tenth decil'] / df_pivot.sum(axis=1)

    # f. Extracting the final column and renaming the index to 'year'
    df_final = df_pivot[['top_10_share']].copy()
    df_final.index.name = 'year'
    
    return df_final