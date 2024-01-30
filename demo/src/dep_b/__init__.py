import pandas as pd

print("INITIALZING dep_b, pd version", pd.__version__)

def get_data():
    s = pd.Series(['a', 'b'], dtype='string')
    assert not hasattr(s, 'case_when')
    return s
