import streamlit as st
import pandas as pd
import numpy as np
import json
import time
import json
#import compound_interest_algorithms
from dateutil.relativedelta import relativedelta

DEBUG_EXPANDER = st.expander("Debug")

########## Cash Class ##########

# Create an cash class that can accept deposits and withdrawals, and earn interest
class Cash:
    def __init__(self, date, amount=0.0, rate=0.0):
        self.rate = rate
        # Create a deposits array with date, amount, recurring frequency of None
        self.deposits = [{
            'start_date': date,
            'end_date': None,
            'amount': amount,
            'frequency': None
        }]
        # Create a datetimeindex with the date, then use that to create a pandas dataframe with the initial amount
        # Directly instantiating a DatetimeIndex
        # self.balances = pd.DataFrame({'deposits': amount}, index=pd.DatetimeIndex([date], name='date', freq='D'))
        # self.balances = pd.DataFrame({'date': datetime_index, 'amount': [amount]}, index=[0])
        # self.balances['deposits'] = amount

    # Create a recurring deposit with amount, start_date, end_date, frequency
    def deposit_recurring(self, amount, start_date, end_date, frequency):
        self.deposits.append({
            'start_date': start_date,
            'end_date': end_date,
            'amount': amount,
            'frequency': frequency
        })

    # Deposit an amount on a given date
    def deposit_once(self, amount, date):
        self.deposit_recurring(amount, date, None, None)

    # Create a recurring withdrawal with amount, start_date, end_date, frequency that calls deposit_recurring with a negative amount
    def withdraw_recurring(self, amount, start_date, end_date, frequency):
        self.deposit_recurring(-amount, start_date, end_date, frequency)
    
    # Withdraw an amount on a given date that calls deposit_once with a negative amount
    def withdraw_once(self, amount, date):
        self.deposit_recurring(-amount, date, None, None)

    # Return a datetime dataframe for all deposits
    def get_deposits(self, start_date, end_date, resample=None):
        # Create a daily series to merge
        df_daily = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))
        df_daily['deposit'] = 0

        # Get indexes for columns
        deposit_index = df_daily.columns.get_loc('deposit')

        # Loop over deposits and add to df_daily
        for deposit in self.deposits:
            DEBUG_EXPANDER.write(deposit)
            # Create a dataframe for this deposit
            if deposit['frequency']:
                dates = pd.date_range(start=deposit['start_date'], end=deposit['end_date'], freq=deposit['frequency'])
                df_recurring = pd.DataFrame({'deposit': deposit['amount']}, index=dates)
            else:
                # dates = pd.date_range(start=deposit['start_date'])
                df_recurring = pd.DataFrame({'deposit': deposit['amount']}, index=pd.DatetimeIndex([deposit['start_date']], name='date', freq='D'))

            # df_recurring['deposit'] = deposit['amount']

            # Add to df_daily
            df_daily = df_daily.add(df_recurring, fill_value=0)

        # Add rate, interest, and total column of zero
        df_daily['rate'] = self.rate
        df_daily['interest'] = 0.0
        df_daily['total'] = 0.0

        # Get indexes for columns
        deposit_index = df_daily.columns.get_loc('deposit')
        rate_index = df_daily.columns.get_loc('rate')
        interest_index = df_daily.columns.get_loc('interest')
        total_index = df_daily.columns.get_loc('total')

        # Calculate interest and total
        # - first day is simply the deposit
        df_daily.iat[0, total_index] = df_daily.iat[0, deposit_index]
        for i in range(1, len(df_daily)):
            # Get previous total
            previous_total = df_daily.iat[i-1, total_index]

            # interest is previous total times daily rate
            df_daily.iat[i, interest_index] = previous_total * (df_daily.iat[i, rate_index] / 365.0)

            # total is previous total plus deposit plus interest
            df_daily.iat[i, total_index] = previous_total + df_daily.iat[i, deposit_index] + df_daily.iat[i, interest_index]

        # Return df_daily, or resample to interval
        if resample is None or resample == "D":
            return df_daily
        else:
            df_resampled = df_daily.resample(resample).first()
            # Recalculate interest as diff between totals
            df_resampled['interest'] = df_resampled['total'].diff()
            return df_resampled
    
    # Withdraw an amount on a given date
    def withdraw(self, date, amount):
        self.deposit(date, -amount)

########## Sidebar ##########

# Create sidebar for variables
with st.sidebar:
    st.subheader("Variables")
    st.date_input("Simulation Start Date", value=pd.Timestamp("2024-01-01"), key='sim_start_date')
    st.date_input("Simulation End Date", value=pd.Timestamp("2025-12-31"), key='sim_end_date')
    st.selectbox("Interest Frequency", ["D", "MS", "QS", "YS"], key='interest_frequency')
    st.selectbox("Interval Frequency", ["D", "MS", "QS", "YS"], key='interval_frequency', index=1)
    st.divider()
    st.number_input("Initial Balance", value=1000, key='initial_balance')
    st.number_input("Interest Rate", value=0.05, key='interest_rate')
    st.divider()
    st.number_input("Recurring Amount", value=100, key='recurring_amount')
    st.date_input("Recurring Start Date", value=pd.Timestamp("2024-02-01"), key='recurring_start_date')
    st.date_input("Recurring End Date", value=pd.Timestamp("2024-11-30"), key='recurring_end_date')
    st.selectbox("Recurring Frequency", ["D", "MS", "QS", "YS"], key='recurring_frequency', index=1)

########## Main App ##########

# Create a cash instance with a $100 deposit and 5% interest on 1/1/2024
my_cash = Cash(
    date=st.session_state.sim_start_date,
    amount=st.session_state.initial_balance,
    rate=st.session_state.interest_rate
)

# Make some deposits and withdrawals
my_cash.deposit_once(amount=500, date='2024-05-15')
my_cash.withdraw_once(amount=250, date='2025-01-01')
# my_cash.deposit(date='2024-03-01', amount=200)
# my_cash.deposit(date='2024-02-01', amount=75)
# my_cash.withdraw(date='2024-02-01', amount=25)
# my_cash.withdraw(date='2024-04-01', amount=100)

# Make recurring deposit and withdrawal
my_cash.deposit_recurring(
    start_date=st.session_state.recurring_start_date,
    end_date=st.session_state.recurring_end_date,
    amount=st.session_state.recurring_amount,
    frequency=st.session_state.recurring_frequency
)
my_cash.withdraw_recurring(
    start_date=st.session_state.recurring_start_date + relativedelta(years=1),
    end_date=st.session_state.recurring_end_date + relativedelta(years=1),
    amount=st.session_state.recurring_amount + 50,
    frequency=st.session_state.recurring_frequency
)

# st.write(my_cash.deposits)
#st.json(json.dumps(my_cash.deposits, indent=2, default=str))
# st.dataframe(my_cash.balances, use_container_width=True)
my_cash_deposits = my_cash.get_deposits(st.session_state.sim_start_date, st.session_state.sim_end_date, st.session_state.interval_frequency)
st.dataframe(my_cash_deposits, use_container_width=True)
st.area_chart(my_cash_deposits, y="total")