import streamlit as st
import pandas as pd
import numpy as np

# Function that takes a start and end date and returns a dataframe of dates and balances
def calculate_balance(start_date, end_date, initial_balance, rate):
    dates = pd.date_range(start=start_date, end=end_date, name='date')
    df = pd.DataFrame(index=dates)
    df['total'] = initial_balance * ((1+(rate/365)) ** ((df.index - df.index[0]) / np.timedelta64(1, 'D')))
    return df


# Calculate total balance and interest for 1 year
# initial_balance = 100
# rate = 0.05
# dates = pd.date_range(start='2024-01-01', end='2024-12-31', name='date')
# df = pd.DataFrame(index=dates)
# df['total'] = initial_balance * ((1+(rate/365)) ** ((df.index - df.index[0]) / np.timedelta64(1, 'D')))
# df['interest'] = df['total'] - initial_balance

# # Display dataframe and area chart
# st.dataframe(df, use_container_width=True)
# st.area_chart(df, y="total")

# # Resample to 1 month intervals and redisplay
# df1 = df.resample("ME").last()
# st.dataframe(df1)
# st.area_chart(df1, y="total")
df_one_year = calculate_balance('2024-01-01', '2024-12-31', 100, 0.05)
df_six_month = calculate_balance('2024-05-01', '2024-12-31', 50, 0.05)

# Merge df_one_year and df_six_month dataframes
# df_merged = pd.merge(df_one_year, df_six_month, how='outer', left_index=True, right_index=True)
df_merged = pd.concat([df_one_year, df_six_month])\
       .groupby('date')['total']\
       .sum()

st.dataframe(df_merged)
st.area_chart(df_merged, y="total")
