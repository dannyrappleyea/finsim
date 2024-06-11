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

dates = pd.date_range(start='2024-01-01', end='2024-12-31', name='Date')
#df = pd.DataFrame(np.random.randint(0, 5, size=len(dates)), index=dates, columns = ['deposit'])
df = pd.DataFrame(index=dates)
df["deposit"] = 1

df["rate"] = 0.05/365.0
# df["interest"] = df["deposit"] * df["rate"]
df['total'] = (df['deposit'] * df['rate'].shift().add(1).cumprod().fillna(1)).cumsum() # From https://stackoverflow.com/questions/57620050/calculate-compound-interest-in-pandas
st.dataframe(df)
st.area_chart(df, y="total")
df1 = df.resample("M").last()
st.dataframe(df1)
st.area_chart(df1)
