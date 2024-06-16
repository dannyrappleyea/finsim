import streamlit as st
import pandas as pd
import numpy as np
import time


# Create an cash class that can accept deposits and withdrawals, and earn interest
class Cash:
    def __init__(self, date, amount=0.0, rate=0.0):
        self.rate = rate

        # Create a datetimeindex with the date, then use that to create a pandas dataframe with the initial amount
        # Directly instantiating a DatetimeIndex
        self.balances = pd.DataFrame({'deposits': amount}, index=pd.DatetimeIndex([date], name='date', freq='D'))
        # self.balances = pd.DataFrame({'date': datetime_index, 'amount': [amount]}, index=[0])
        # self.balances['deposits'] = amount

    # Deposit an amount on a given date
    def deposit(self, date, amount):
        if date in self.balances.index:
            self.balances.at[date, 'deposits'] += amount
        else:
            df = pd.DataFrame({'deposits': amount}, index=pd.DatetimeIndex([date], name='date', freq='D'))
            self.balances = pd.concat([self.balances, df])
            self.balances.sort_index(inplace=True)

    # Withdraw an amount on a given date
    def withdraw(self, date, amount):
        self.deposit(date, -amount)

    def calculate_interest(self):
        self.interest = self.balance * self.rate/365

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
    df_recurring['deposit'] = recurring_amount

    # Create a daily series to merge
    dates = pd.date_range(start=start_date, end=end_date, name='date')
    df_daily = pd.DataFrame(index=dates)
    df_daily['deposit'] = 0

    # Update the daily dataframe from the recurring dataframe
    df_daily.update(df_recurring)
    df = df_daily

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

# Calculate recurring interest as individual series
def calculate_recurring_balance_series(start_date, end_date, recurring_amount, frequency, rate):
    # Create a date range for the recurring amount
    dates_recurring = pd.date_range(start=start_date, end=end_date, freq=frequency, name='date')
    # df_recurring = pd.DataFrame(index=dates)
    # df_recurring['deposit'] = recurring_amount

    # Create a daily series to merge
    dates_daily = pd.date_range(start=start_date, end=end_date, name='date')
    df_daily = pd.DataFrame(index=dates_daily)
    df_daily['total'] = 0
    # df_daily['deposit'] = 0

    # Loop over dates_recurring
    for i in range(len(dates_recurring)):
        date = dates_recurring[i]
        #st.write(dates_recurring[i])
        
        # Get a dataframe from calculate_balance for this date
        df = calculate_balance(date, end_date, recurring_amount, rate)
        # df = df.rename(columns={"total": date})
        #st.dataframe(df, use_container_width=True)

        # Add with df_daily
        df_daily = df_daily.add(df, fill_value=0)
    
    # Calculate total
    # df_total = df_daily.sum(axis=1)
    # df_total.name = 'total'
    # return df_total
    return df_daily

# Calculate compound interest with recurring amounts using offsets
def calculate_recurring_balance_offset(start_date, end_date, recurring_amount, frequency, rate):
    dates = pd.date_range(start=start_date, end=end_date, freq=frequency, name='date')
    df_recurring = pd.DataFrame(index=dates)
    df_recurring['deposit'] = recurring_amount

    # Create a daily series to merge
    dates = pd.date_range(start=start_date, end=end_date, name='date')
    df_daily = pd.DataFrame(index=dates)
    df_daily['deposit'] = 0
    df_daily['total'] = 0

    # Update the daily dataframe from the recurring dataframe
    df_daily.update(df_recurring)

    # Get all rows with a deposit
    df_deposits = df_daily[df_daily['deposit'] > 0]

    # Look over deposits
    is_first_deposit = True
    last_row = None
    last_total = 0
    for row in df_deposits.index.to_list():
        # st.write(row)
        if is_first_deposit:
            # First deposit
            df_daily.loc[row, 'total'] = df_daily.loc[row, 'deposit']
            # st.dataframe(df_daily.loc[row:row], use_container_width=True)
            is_first_deposit = False
            last_row = row
            last_total = df_daily.loc[row, 'total']
        else:   # Calculate total between current row and last row
            # st.dataframe(df_daily.loc[last_row:row], use_container_width=True)

            # Calculate the balance between the two dates
            df_slice = calculate_balance(last_row, row, last_total, rate)

            # Update df_daily with new total
            df_daily.update(df_slice)

            # Update last total with the deposit
            last_total = df_daily.loc[row, 'total'] + df_daily.loc[row, 'deposit']
            df_daily.loc[row, 'total'] = last_total

            #st.dataframe(df_slice, use_container_width=True)
            # st.dataframe(df_daily.loc[last_row:row], use_container_width=True)
            last_row = row

    # Calculate total between last row and end date    
    # st.write(end_date)
    # st.dataframe(df_daily.loc[last_row:end_date], use_container_width=True)
    df_slice = calculate_balance(last_row, end_date, last_total, rate)
    df_daily.update(df_slice)
    # st.dataframe(df_daily.loc[last_row:end_date], use_container_width=True)

    # Return df_daily
    return df_daily

# Create sidebar for variables
with st.sidebar:
    st.subheader("Variables")
    st.date_input("Simulation Start Date", value=pd.Timestamp("2024-01-01"), key='sim_start_date')
    st.date_input("Simulation End Date", value=pd.Timestamp("2029-12-31"), key='sim_end_date')
    st.number_input("Initial Balance", value=1000, key='initial_balance')
    st.number_input("Interest Rate", value=0.05, key='interest_rate')
    st.selectbox("Frequency", ["D", "M", "Q", "Y"], key='interest_frequency')
    st.divider()
    st.number_input("Recurring Amount", value=100, key='recurring_amount')
    st.selectbox("Recurring Frequency", ["D", "M", "Q", "Y"], key='recurring_frequency', index=1)

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
# Elapsed time: 0.054891109466552734 seconds (1 year)
# Elapsed time: 0.5093100070953369 seconds (10 years)
# Elapsed time: 2.3993027210235596 seconds (50 years)
# Elapsed time: 4.634013891220093 seconds (100 years)
# - improved time through iat
# t1 = time.time()
# df_one_year = calculate_recurring_balance_loop('2024-01-01', '2074-12-31', 100, "MS", 0.05)
# t2 = time.time()
# st.write('Elapsed time: {} seconds'.format((t2 - t1)))

# st.dataframe(df_one_year, use_container_width=True)
# st.area_chart(df_one_year, y="total")

### Example showing recurring deposit series. Get time before and after function, then show elapsed time
# Elapsed time: 0.022956132888793945 seconds (1 year)
# Elapsed time: 0.2656688690185547 seconds (10 years)
# Elapsed time: 1.994513988494873 seconds (50 years)
# Elapsed time: 5.548826694488525 seconds (100 years)
# t1 = time.time()
# df_one_year = calculate_recurring_balance_series('2024-01-01', '2024-12-31', 100, "MS", 0.05)
# t2 = time.time()
# st.write('Elapsed time: {} seconds'.format((t2 - t1)))

# st.dataframe(df_one_year, use_container_width=True)
# st.area_chart(df_one_year, y="total")

### Example showing recurring deposit series. Get time before and after function, then show elapsed time
# Elapsed time: 0.04046988487243652 seconds (1 year)
# Elapsed time: 0.3547549247741699 seconds (10 years)
# Elapsed time: 1.913755178451538 seconds (50 years)
# Elapsed time: 4.166244268417358 seconds (100 years)
# t1 = time.time()
# df_one_year = calculate_recurring_balance_offset('2024-01-01', '2024-12-31', 100, "MS", 0.05)
# t2 = time.time()
# st.write('Elapsed time: {} seconds'.format((t2 - t1)))

# st.dataframe(df_one_year, use_container_width=True)
# st.area_chart(df_one_year, y="total")

# Create a cash instance with a $100 deposit and 5% interest on 1/1/2024
my_cash = Cash(
    date=st.session_state.sim_start_date,
    amount=st.session_state.initial_balance,
    rate=st.session_state.interest_rate
)

# Make a deposit on 2/1/2024 for $200
my_cash.deposit(date='2024-01-01', amount=50)
my_cash.deposit(date='2024-03-01', amount=200)
my_cash.deposit(date='2024-02-01', amount=75)
my_cash.withdraw(date='2024-02-01', amount=25)
my_cash.withdraw(date='2024-04-01', amount=100)

st.dataframe(my_cash.balances, use_container_width=True)