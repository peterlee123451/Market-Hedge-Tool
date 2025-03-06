import streamlit as st
import pandas as pd
import pandas_datareader as pdr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta




def main():

    st.title("Market Hedge Tool")

    with st.sidebar:
        st.header("Parameters") #Config/ param setting here
        stock_ticker = st.text_input("Enter a stock ticker:", None)
        start_date = st.date_input("Enter a start date", None)
        MV_position = st.text_input("Enter the market value of the position:", None)


        if stock_ticker:
            end_date = datetime.date.today().date()

            try:
                df = pdr.DataReader(stock_ticker, 'yahoo', start_date, end_date)
                df2 = pdr.DataReader("^SPX", 'yahoo', start_date, end_date)
                df['Log_Returns'] = np.log(df['Adj Close']/ df['Adj Close'].shift(1))
                df2['Log_Returns'] = np.log(df2['Adj Close']/ df2['Adj Close'].shift(1))
                log_returns_stock = df[['Log_Returns']].dropna()
                log_returns_market = df2[['Log_Returns']].dropna()
                beta = np.cov(log_returns_stock['Log_Returns'], log_returns_market['Log_Returns'])[0][1] / np.var(log_returns_market['Log_Returns'])
                futures_value = pdr.DataReader("ES=F", 'yahoo', end_date-timedelta(days = 3), end_date)
                futures_value = futures_value['Adj Close'].iloc[-1]
                delta = float(MV_position) * beta
                hedge_ratio = delta / futures_value

                fig, ax = plt.subplots()
                ax.plot(log_returns_stock.index, log_returns_stock, label=f'{stock_ticker} Log Returns')
                ax.plot(log_returns_market.index, log_returns_market, label='S&P 500 Log Returns')
                ax.set_title("Log Returns Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel("Log Returns")
                ax.legend()
            
                # Display the plot and the hedge ratio in the main body
                st.pyplot(fig)
                st.write(f"**Hedge Ratio:** {hedge_ratio:.4f}")
            
            except Exception as e:
                st.write(f"Error: {e}")

if __name__ == '__main__':
    main()



                












