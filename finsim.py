import streamlit as st
import pandas as pd
import numpy as np
import json
import time
import json
import compound_interest_algorithms


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
        self.balances = pd.DataFrame({'deposits': amount}, index=pd.DatetimeIndex([date], name='date', freq='D'))
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
    def deposit(self, date, amount):
        self.deposit_recurring(amount, date, None, None)
        # if date in self.balances.index:
        #     self.balances.at[date, 'deposits'] += amount
        # else:
        #     df = pd.DataFrame({'deposits': amount}, index=pd.DatetimeIndex([date], name='date', freq='D'))
        #     self.balances = pd.concat([self.balances, df])
        #     self.balances.sort_index(inplace=True)
    
    # Return a datetime dataframe for all deposits
    def get_deposits(self, start_date, end_date):
        # Create a daily series to merge
        df_daily = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))
        df_daily['deposit'] = 0

        # Get indexes for columns
        deposit_index = df_daily.columns.get_loc('deposit')

        # Loop over deposits and add to df_daily
        for deposit in self.deposits:
            st.write(deposit)
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

        # return df_daily
        return df_daily

    # Withdraw an amount on a given date
    def withdraw(self, date, amount):
        self.deposit(date, -amount)

    def calculate_interest(self):
        self.interest = self.balance * self.rate/365

########## Sidebar ##########

# Create sidebar for variables
with st.sidebar:
    st.subheader("Variables")
    st.date_input("Simulation Start Date", value=pd.Timestamp("2024-01-01"), key='sim_start_date')
    st.date_input("Simulation End Date", value=pd.Timestamp("2024-12-31"), key='sim_end_date')
    st.number_input("Initial Balance", value=1000, key='initial_balance')
    st.number_input("Interest Rate", value=0.05, key='interest_rate')
    st.selectbox("Frequency", ["D", "M", "Q", "Y"], key='interest_frequency')
    st.divider()
    st.number_input("Recurring Amount", value=100, key='recurring_amount')
    st.date_input("Recurring Start Date", value=pd.Timestamp("2024-02-01"), key='recurring_start_date')
    st.date_input("Recurring End Date", value=pd.Timestamp("2024-11-30"), key='recurring_end_date')
    st.selectbox("Recurring Frequency", ["D", "MS", "Q", "Y"], key='recurring_frequency', index=1)

########## Main App ##########

# Create a cash instance with a $100 deposit and 5% interest on 1/1/2024
my_cash = Cash(
    date=st.session_state.sim_start_date,
    amount=st.session_state.initial_balance,
    rate=st.session_state.interest_rate
)

# Make some deposits and withdrawals
# my_cash.deposit(date='2024-01-01', amount=50)
# my_cash.deposit(date='2024-03-01', amount=200)
# my_cash.deposit(date='2024-02-01', amount=75)
# my_cash.withdraw(date='2024-02-01', amount=25)
# my_cash.withdraw(date='2024-04-01', amount=100)

# Make recurring deposit
my_cash.deposit_recurring(
    start_date=st.session_state.recurring_start_date,
    end_date=st.session_state.recurring_end_date,
    amount=st.session_state.recurring_amount,
    frequency=st.session_state.recurring_frequency
)

# st.write(my_cash.deposits)
#st.json(json.dumps(my_cash.deposits, indent=2, default=str))
# st.dataframe(my_cash.balances, use_container_width=True)
st.dataframe(my_cash.get_deposits(st.session_state.sim_start_date, st.session_state.sim_end_date), use_container_width=True)