import pandas as pd
from fredapi import Fred

def load_fred_states(fred, states, suffix):
    """ download one FRED series per state and collect them into a wide DataFrame

    Follows the FRED recipe from lecture 07_08 (02_From_API): get_series ->
    resample to annual -> collect -> year index.

    Args:
        fred (fredapi.Fred): an authenticated FRED client
        states (list): two-letter state codes (STATES from states.py)
        suffix (str): FRED series suffix, 'RGSP' (real GDP) or 'POP' (population)

    Returns:
        df (pandas.DataFrame): years in the index, state codes in the columns
    """
    data = {}
    
    for state in states:                    # a. loop over the 50 states
        code = f'{state}{suffix}'           # b. build the FRED series name, e.g. 'ALRGSP'
        s = fred.get_series(code)           # c. download the series
        s = s.resample('YS').mean()         # d. enforce annual frequency (year-start)
        data[state] = s                     # e. store with the state code as key
    df = pd.DataFrame(data)                 # f. states -> columns, dates -> index
    df.index = df.index.year               # g. keep the year only
    df = df.rename_axis('year')            # h. name the index 'year'
    return df