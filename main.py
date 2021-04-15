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
    st.sidebar.markdown("---")



#################### MAIN PAGE FUNCTIONS ####################

def show_linreg_setup():
    st.markdown('')
    st.markdown('---')
    st.markdown("""<div style='text-align: center;'><h3><b>REGRESSION CHART</b></h3></div>""", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center;'>Perform linear regression analysis to see estimated \
         price for the stock.</div>""", unsafe_allow_html=True)

# Get historical market data
@st.cache
def load_data(ticker):
    start = "1950-01-01" #max time period
    stop = date.today().strftime("%Y-%m-%d") #today
    # download data from start to today's data
    data = yf.download(ticker, start, stop) # returns a pandas df
    # make date column as first column of dataframe
    data.reset_index(inplace=True)
    return data


def plot_historical_chart(ticker, data):
    fig = go.Figure(data=[go.Candlestick(x=data['Date'],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'])
    ])
    
    fig.layout.update(xaxis_rangeslider_visible=True, height=750,\
        title = f"<b>Stock: {ticker}</b>")    
    # y-axis
    fig.update_yaxes(title_text='Price (USD)')
    # plot
    config={'modeBarButtonsToAdd': ['drawline']}
    st.plotly_chart(fig, use_container_width=True, config=config)


# Forecasting
# for linear regression
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression

@st.cache
def update_data(data, start, stop):
    start_date = start+"-01-01"
    stop_date = stop + "-12-31"
    new_data = data[(data.Date>=start_date) & (data.Date<=stop_date)]
    return new_data

@st.cache
def run_linear_regression(data):
    data = data.reset_index() #make 'Date' column and have integers in index
    x = np.array(data.index).reshape(-1,1)
    y = data['Open']
    model = LinearRegression().fit(x,y)
    model_pred = model.predict(x)
    model_x = data.index
    return (model_x, model_pred)

def plot_linreg(data, model_pred, ticker):
    #lin reg line plot
    fig = go.Figure(data=[go.Scatter(x=data.Date, y=model_pred, name="Regression Price", line_color='#73BAD7')])
    fig.layout.update(xaxis_rangeslider_visible=True, height=750,\
        title_text = f"<b>Stock: {ticker}</b>")  
    fig.update_yaxes(title_text='Price (USD)')  
    #open price line plot
    fig.add_trace(go.Scatter(x=data.Date, y=data.Open, name="Open Price", line_color='orange'))
    config={'modeBarButtonsToAdd': ['drawline']}
    st.plotly_chart(fig, use_container_width=True, config=config)





#################### MAIN PROGRAM ####################

#------------------------SETUP-----------------------#
st.set_page_config(layout="wide") #wide width of page 

# Load ticker symbols
alltickers_df = pd.read_csv("AllTickers.csv")
tickers = list(alltickers_df['Symbol'])

# Main Page 
st.markdown("""<div style='text-align: center;'><h1>THE STOCK FORECAST 📈</h1></div>""", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""<div style='text-align: center;'><h3><b>HISTORICAL CHART</b></h3></div>""", unsafe_allow_html=True)
st.markdown("""<div style='text-align: center;'>View a candlestick chart with historical \
    daily prices of the stock.</div>""", unsafe_allow_html=True)
st.markdown("")

# Sidebar
st.sidebar.markdown("""<h3 style='text-align: center;'>SEARCH 🔎</h3>""", unsafe_allow_html=True)
ticker = st.sidebar.text_input("") #search box
st.sidebar.markdown("")
st.sidebar.markdown("")
st.sidebar.markdown("""<h3 style='text-align: center;'>SUMMARY</h3>""", unsafe_allow_html=True)


#---------------------RUN PROGRAM--------------------#

# format user input to make it uppercase
if not ticker.isupper():
    ticker = ticker.upper()

# if no ticker entered
if not ticker: 
    st.sidebar.markdown('')
    st.sidebar.markdown("""<div style='text-align: center;'>Please search a ticker to see results.</div>""", unsafe_allow_html=True)
    show_linreg_setup()

# if ticker not in available list
elif ticker not in tickers:
    st.sidebar.markdown("")
    st.sidebar.markdown(f"""<div style='text-align: center;'>The ticker symbol <b>{ticker}</b> was not found \
        in our database.</div>""", unsafe_allow_html=True)
    st.sidebar.markdown("")
    st.sidebar.markdown("""<div style='text-align: center;'>Please search something else.</div>""", unsafe_allow_html=True)
    show_linreg_setup()
    
# if available ticker provided
else: 
    # Sidebar
    st.sidebar.markdown('---')
    display_summary(ticker)
    # Historical chart
    data = load_data(ticker)
    plot_historical_chart(ticker, data)
    # Regression
    show_linreg_setup()
    # get earliest year and most recent year from data set
    min_start, max_stop = data.Date.iloc[0].year, data.Date.iloc[-1].year
    # user selects range of years for regression data
    start_stop = st.slider("SELECT RANGE OF YEARS:", min_start, max_stop, (min_start,max_stop))
    start, stop = str(start_stop[0]), str(start_stop[1])
    new_data = update_data(data, start, stop)
    # plot regression when button is clicked
    if st.button('SHOW REGRESSION'):
        model_x, model_pred = run_linear_regression(new_data)
        plot_linreg(new_data, model_pred, ticker)
 
