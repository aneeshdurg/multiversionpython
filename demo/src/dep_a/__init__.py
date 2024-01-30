import pandas as pd

print("INITIALZING dep_a, pd version", pd.__version__)

def get_data():
    s = pd.Series(['a', 'b'], dtype='string')
    assert hasattr(s, 'case_when')
    return s
