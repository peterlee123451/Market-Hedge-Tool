import streamlit as st
import pandas as pd
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def main():
    st.title("Market Hedge Tool")

    with st.sidebar:
        st.header("Parameters")
        stock_ticker = st.text_input("Enter a stock ticker:", key="stock_ticker")
        start_date = st.date_input("Enter a start date", key="start_date")
        MV_position = st.text_input("Enter the market value of the position:", key="MV_position")
        
        execute_button = st.button("Execute")
        clear_button = st.button("Clear")

        if clear_button:
            st.session_state.stock_ticker = ""
            st.session_state.start_date = datetime.today().date()
            st.session_state.MV_position = ""
            st.experimental_rerun()

    if execute_button:
        if not stock_ticker or not start_date or not MV_position:
            st.error("Please provide all inputs!")
        else:
            try:
                end_date = datetime.today().date()

                df = pdr.DataReader(stock_ticker, 'yahoo', start_date, end_date)
                df2 = pdr.DataReader("^SPX", 'yahoo', start_date, end_date)

                df['Log_Returns'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
                df2['Log_Returns'] = np.log(df2['Adj Close'] / df2['Adj Close'].shift(1))
                log_returns_stock = df[['Log_Returns']].dropna()
                log_returns_market = df2[['Log_Returns']].dropna()

                beta = np.cov(log_returns_stock['Log_Returns'], log_returns_market['Log_Returns'])[0][1] / np.var(log_returns_market['Log_Returns'])

                futures_data = pdr.DataReader("ES=F", 'yahoo', end_date - timedelta(days=3), end_date)
                futures_value = futures_data['Adj Close'].iloc[-1]

                delta = float(MV_position) * beta
                hedge_ratio = delta / futures_value

                fig, ax = plt.subplots()
                ax.plot(log_returns_stock.index, log_returns_stock, label=f'{stock_ticker} Log Returns')
                ax.plot(log_returns_market.index, log_returns_market, label='S&P 500 Log Returns')
                ax.set_title("Log Returns Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel("Log Returns")
                ax.legend()

                st.pyplot(fig)
                st.write(f"**Hedge Ratio:** {hedge_ratio:.4f}")

            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == '__main__':
    main()
