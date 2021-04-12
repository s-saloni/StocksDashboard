""" Streamlit-based web app to view stock data from Yahoo Finance
"""

# libraries 
import streamlit as st
from datetime import date
import yfinance as yf

import numpy as np
import pandas as pd
from plotly import graph_objects as go

import requests
from bs4 import BeautifulSoup


#################### SIDEBAR FUNCTIONS ####################
# Function to scrape info on ticker
@st.cache
def get_info(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    # locations of values, all have same class
    indices = [0, 1, 5, 13, 8, 10, 11]
    info = [soup.find_all('td', {'class': "Ta(end) Fw(600) Lh(14px)"})[i].text for i in indices]
    company = soup.find_all('h1', {'class': "D(ib) Fz(18px)"})[0].text
    name_len = len(company) - (len(ticker) + 2) #remove ticker at end
    info.insert(0, company[:name_len]) #add company name at front
    return info

# Function to display values and their names
def display_summary(ticker):
    # scrape info on the ticker
    info = get_info(ticker)
    info_names = ["Name: ", "Close Price: ", "Open Price: ", "52-Week Range: ", "Dividend Rate & Yield: ", \
        "Market Cap: ", "PE Ratio: ", "EPS: "]
    # print out info in sidebar
    for name,infoValue in zip(info_names, info):
        row = \
        f"""<div> 
                <span style='float: left;'><b>{name}</b></span>
                <span style='float: right;'> {infoValue}</span>
            </div>
        """
        st.sidebar.markdown(row, unsafe_allow_html=True)
        #st.sidebar.markdown(f"""**{name}** {infoValue}""")
    st.sidebar.markdown("---")



#################### MAIN PAGE FUNCTIONS ####################

# Get historical market data
@st.cache
def load_data(ticker):
    START = "1900-01-01" #max time period
    TODAY = date.today().strftime("%Y-%m-%d")
    # download data from start to today's data
    data = yf.download(ticker, START, TODAY) # returns a pandas df
    # make date column as first column of dataframe
    data.reset_index(inplace=True)
    return data


def plot_historical_chart(ticker):
    fig = go.Figure(data=[go.Candlestick(x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'])
    ])
    
    fig.layout.update(xaxis_rangeslider_visible=True, height=750,\
        title = f"<b>HISTORICAL CHART: {ticker}</b>")    
    # y-axis
    fig.update_yaxes(title_text='Price ($USD)')
    # plot
    config={'modeBarButtonsToAdd': ['drawline']}
    st.plotly_chart(fig, use_container_width=True, config=config)


# Forecasting
# for linear regression
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression

def linreg(data):
    pass    






#################### MAIN PROGRAM ####################

#------------------------SETUP-----------------------#
st.set_page_config(layout="wide") #wide width of page 

# Load ticker symbols
alltickers_df = pd.read_csv("AllTickers.csv")
tickers = list(alltickers_df['Symbol'])

# Main Page 
st.markdown("""<h1 style='text-align: center;'>The Stock Forecast</h1>""", unsafe_allow_html=True)
#st.markdown("---")

# Sidebar
st.sidebar.markdown("""<h3 style='text-align: center;'>SEARCH</h3>""", unsafe_allow_html=True)
ticker = st.sidebar.text_input("") # search box
st.sidebar.markdown("---")
st.sidebar.markdown("""<h3 style='text-align: center;'>SUMMARY</h3>""", unsafe_allow_html=True)
st.sidebar.markdown("")

#---------------------RUN PROGRAM--------------------#

# format user input to make it uppercase
if not ticker.isupper():
    ticker = ticker.upper()

# if no ticker entered
if not ticker: 
    st.sidebar.markdown("Please search a ticker to see results.")

# if ticker not in available list
elif ticker not in tickers:
    st.sidebar.markdown("There was no ticker called **" + ticker + "** found in our database.")
    st.sidebar.markdown("Please search something else.")
    
# if available ticker provided
else: 
    display_summary(ticker)
    data = load_data(ticker)
    plot_historical_chart(ticker)

