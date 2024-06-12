import streamlit as st
import pandas as pd
import numpy as np

# Calculate total balance and interest for 1 year
initial_balance = 100
rate = 0.05
dates = pd.date_range(start='2024-01-01', end='2024-12-31', name='date')
df = pd.DataFrame(index=dates)
df['total'] = initial_balance * ((1+(rate/365)) ** ((df.index - df.index[0]) / np.timedelta64(1, 'D')))
df['interest'] = df['total'] - initial_balance

# Display dataframe and area chart
st.dataframe(df, use_container_width=True)
st.area_chart(df, y="total")

# Resample to 1 month intervals and redisplay
df1 = df.resample("ME").last()
st.dataframe(df1)
st.area_chart(df1, y="total")
