import streamlit as st
import pandas as pd
import numpy as np
import time

# Function that takes a start and end date, calculates compound interest and returns a dataframe of dates and balances
def calculate_balance(start_date, end_date, initial_balance, rate):
    dates = pd.date_range(start=start_date, end=end_date, name='date')
    df = pd.DataFrame(index=dates)
    df['total'] = initial_balance * ((1+(rate/365)) ** ((df.index - df.index[0]) / np.timedelta64(1, 'D')))
    return df

# Function that calculates compound interest for a recurring monthly deposit
# - takes a start and end date, recurring amount, and interest rate
# - returns a dataframe of dates and balances
def calculate_recurring_balance(start_date, end_date, recurring_amount, rate):
    dates = pd.date_range(start=start_date, end=end_date, name='date')
    df = pd.DataFrame(index=dates)
    # From https://www.thecalculatorsite.com/finance/calculators/compound-interest-formula
    # PMT × (((1 + r/n)^(nt) - 1) / (r/n)) × (1+r/n)
    # df["days"] = (df.index - df.index[0]) / np.timedelta64(1, 'D')
    df['total'] = recurring_amount * ((( (1+(rate/365)) ** ((df.index - df.index[0]) / np.timedelta64(1, 'D')))) - 1) / (rate/365) * (1+(rate/365))
    return df

# Function that calculates compound interest for a recurring monthly deposit
# - takes a start and end date, recurring amount frequency, and interest rate
# - returns a dataframe of dates and balances
def calculate_recurring_balance_loop(start_date, end_date, recurring_amount, frequency, rate):
    dates = pd.date_range(start=start_date, end=end_date, freq=frequency, name='date')
    df_recurring = pd.DataFrame(index=dates)
    df_recurring['total'] = recurring_amount

    # Create a daily series to merge
    dates = pd.date_range(start=start_date, end=end_date, name='date')
    df_daily = pd.DataFrame(index=dates)
    df_daily['total'] = 0

    # Merge the two dataframes with default value of zero, summing the total field from each into a new total field
    df = pd.merge(df_daily, df_recurring, how='outer', left_index=True, right_index=True)
    #df['total_y'].fillna(value=0, inplace=True)
    df['total_y'] = df['total_y'].fillna(0)
    df['deposit'] = df['total_x'] + df['total_y']
    df = df.drop(['total_x', 'total_y'], axis=1)

    # Add interest and total column of zero
    df['interest'] = 0
    df['total'] = 0

    # Get indexes for columns
    deposit_index = df.columns.get_loc('deposit')
    interest_index = df.columns.get_loc('interest')
    total_index = df.columns.get_loc('total')

    # Calculate interest and total
    # df['total'].iloc[0] = df['deposit'].iloc[0]
    df.iat[0, total_index] = df.iat[0, deposit_index]
    for i in range(1, len(df)):
        # df['interest'].iloc[i] = df['total'].iloc[i-1] * rate / 365
        # df.loc[i, 'interest'] = df.loc[i-1, 'total'] * rate / 365
        df.iat[i, interest_index] = df.iat[i-1, total_index] * rate / 365

        #df['total'].iloc[i] = df['deposit'].iloc[i] + df['total'].iloc[i-1] + df['interest'].iloc[i]
        #df.loc[i, 'total'] = df.loc[i, 'deposit'] + df.loc[i-1, 'total'] + df.loc[i, 'interest']
        df.iat[i, total_index] = df.iat[i, deposit_index] + df.iat[i-1, total_index] + df.iat[i, interest_index]

    return df


# # Resample to 1 month intervals and redisplay
# df1 = df.resample("ME").last()
# st.dataframe(df1)
# st.area_chart(df1, y="total")


# Example showing two merges
# df_one_year = calculate_recurring_balance('2024-01-01', '2024-12-31', 100, 0.05)
# df_six_month = calculate_balance('2024-05-01', '2024-12-31', 50, 0.05)

# # Merge df_one_year and df_six_month dataframes
# df_merged = pd.merge(df_one_year, df_six_month, how='outer', left_index=True, right_index=True)
# total = df_merged.sum(axis=1)
# # df_merged = pd.concat([df_one_year, df_six_month])\
# #        .groupby('date')['total']\
# #        .sum()

# st.dataframe(df_merged, use_container_width=True)
# st.area_chart(total)


# ### Example showing recurring deposit. Get time before and after function, then show elapsed time
# Elapsed time: 0.0020020008087158203 seconds
# - issue is that deposit frequency and interest frequency must be the same
# t1 = time.time()
# df_one_year = calculate_recurring_balance('2024-01-01', '2030-12-31', 100, 0.05)
# t2 = time.time()
# st.write('Elapsed time: {} seconds'.format((t2 - t1)))

# st.dataframe(df_one_year, use_container_width=True)
# st.area_chart(df_one_year, y="total")

### Example showing recurring deposit loop. Get time before and after function, then show elapsed time
# Elapsed time: 0.054891109466552734 seconds
# - improved time through iat
t1 = time.time()
df_one_year = calculate_recurring_balance_loop('2024-01-01', '2024-12-31', 100, "MS", 0.05)
t2 = time.time()
st.write('Elapsed time: {} seconds'.format((t2 - t1)))

st.dataframe(df_one_year, use_container_width=True)
st.area_chart(df_one_year, y="total")