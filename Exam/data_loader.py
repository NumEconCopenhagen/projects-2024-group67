# Calling the fred-API and the states .py file for translating the state codes. 
import pandas as pd
from fredapi import Fred
from states import STATES   

# Constructing the data load function: 
def load_state_data(api_key):
    """ download real GDP and population for all 50 states from FRED

    Args:
        api_key (str): a 32-character FRED API key

    Returns:
        df_gdp (pandas.DataFrame): real GDP, millions of dollars,
            years in the index and state codes in the columns
        df_pop (pandas.DataFrame): population, thousands of persons,
            same shape as df_gdp
    """

    # a. Calling our FRED API key for validating the data extraction. 
    fred = Fred(api_key=api_key)

    # b. collecting one series for each state, where the columns are the states and the dates are used as index.
    gdp, pop = {}, {}
    for state in STATES: # loops through each state and extracts the data
        gdp[state] = fred.get_series(f'{state}RGSP').resample('YS').mean()  # real GDP
        pop[state] = fred.get_series(f'{state}POP').resample('YS').mean()   # population

    # c. building the two data frames
    df_gdp = pd.DataFrame(gdp)
    df_pop = pd.DataFrame(pop)

    # d. keeping the year and naming the index
    for df in (df_gdp, df_pop):
        df.index = df.index.year
        df.index.name = 'year'

    return df_gdp, df_pop
