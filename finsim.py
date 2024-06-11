import streamlit as st
import pandas as pd
import numpy as np


# dates = pd.date_range(start='2024-01-01', end='2024-12-31', name='Date')
# df = pd.DataFrame(np.random.randint(0, 10, size=len(dates)), index=dates, columns = ['value'])
# df1 = df.resample("M").sum()
# st.dataframe(df1)
# st.area_chart(df1)
# st.area_chart(df)

#ts = pd.Series(np.random.randint(0, 10, size=len(dates)), index=dates)
#ts.resample("ME").sum()
#st.area_chart(ts.resample("ME").sum())

initial_balance = 100
rate = 0.05
dates = pd.date_range(start='2024-01-01', end='2024-12-31', name='date')
#df = pd.DataFrame(np.random.randint(0, 5, size=len(dates)), index=dates, columns = ['deposit'])
df = pd.DataFrame(index=dates)
df["numdays"] = (df.index - df.index[0]) / np.timedelta64(1, 'D')
# df["balance"] = initial_balance * 

# df.at['2024-01-01', 'deposit'] = 100
# df["deposit"] = 0

# df["rate"] = 0.05/365.0
# df["interest"] = df["deposit"] * df["rate"]
# df['total'] = (df['deposit'] * df['rate'].shift().add(1).cumprod().fillna(1)).cumsum() # From https://stackoverflow.com/questions/57620050/calculate-compound-interest-in-pandas
df['total'] = initial_balance * ((1+(rate/365)) ** (365 * (df["numdays"]/365)))
st.dataframe(df, use_container_width=True)
st.area_chart(df, y="total")
df1 = df.resample("ME").last()
st.dataframe(df1)
st.area_chart(df1)
