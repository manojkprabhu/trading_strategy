# Strategy BarUpDn: If current open price is greater than last close 
# and current close price is greater than today's open,
# make a trade.

import pandas as pd
import plotly.graph_objects as go
import plotly.offline as offline
import numpy as np
import math
   
data = pd.read_csv('data_binance.csv')

data_types = {'open_price': float, 'high': float, 'low': float, 'close': float}

data['time'] = pd.to_datetime(data['time'])

data = data.astype(data_types)

data = data.head(200) 
# print(data)

short_sma_period = 3
long_sma_period = 6

equity= 10000
risk_percent = 50
STOP_LOSS_PERCENT = 5
TAKE_PROFIT_PERCENT = 17

data['short_sma'] = data['close'].rolling(window=short_sma_period).mean()
data['long_sma'] = data['close'].rolling(window=long_sma_period).mean()

entry_price = None

#BarUp BULL CALL
data['entry_signal_bull'] = (data['short_sma'].shift() < data['long_sma'].shift()) & (data['short_sma'] > data['long_sma']).astype(int)
data['exit_signal_bull'] = 0

for index, row in data.iterrows():
    if (entry_price == None) and (row['entry_signal_bull'] == 1):
        entry_price = row['close']
    else:
        if(entry_price == None):
            continue;
        # print(entry_price)
        if (row['close'] >= (entry_price * (1 + TAKE_PROFIT_PERCENT/100))) | (row['close'] <= (entry_price * (1 - STOP_LOSS_PERCENT/100))):
            data.at[index, "exit_signal_bull"] = 1
            entry_price = None
        else:
            continue

# entry_signal_1 = data[data["entry_signal_bull"] == 1].reset_index(drop=False)
# print(entry_signal_1)

# print(data[["open_price", "close", "entry_signal_bull", "exit_signal_bull"]])

# print(data)
# print(data['exit_signal_bull'])

position_size_bull = []

for index, row in data.iterrows():
    if row['entry_signal_bull'] == 1:
        amt_per_trade = equity * (risk_percent/100)
        position_size_bull.append(math.floor(amt_per_trade /row['close']))
    else:
        position_size_bull.append(0)
        
        
data['position_size_bull'] = position_size_bull

position = 0
total_profit_bull = 0
entry_price = None
position_qty = 0


for i, row in data.iterrows():
    if row['exit_signal_bull'] == 1:
        if position != 0 and entry_price != None:
            exit_price = row['close']                      
            profit = (exit_price - entry_price) * position_qty #* position_qty #if position == 1 else (entry_price - exit_price)
            total_profit_bull += profit
            position = 0  # No position
            position_qty = 0
            
           
    if row['entry_signal_bull'] == 1:
        if position == 0:
            position = 1  
            entry_price = row['close']
            position_qty = row['position_size_bull']


print("total_profit_bull: " + str(total_profit_bull))

###--------------####-----------------###--------------###--------###

entry_price = None
position = 0

#BarDn BEAR CALL
data['entry_signal_bear'] = (data['short_sma'].shift() > data['long_sma'].shift()) & (data['short_sma'] < data['long_sma']).astype(int)
data['exit_signal_bear'] = 0

for index, row in data.iterrows():
    if (entry_price == None) and (row['entry_signal_bear'] == 1):
        entry_price = row['close']
    else:
        if(entry_price == None):
            continue;
        # print(entry_price)
        else:
            if (row['close'] >= (entry_price * (1 - TAKE_PROFIT_PERCENT/100))): # | (row['close'] <= (entry_price * (1 + STOP_LOSS_PERCENT/100))):
                data.at[index, "exit_signal_bear"] = 1
                row['exit_signal_bear'] = 1
                entry_price = None
            else:
                continue

# print(data[['exit_signal_bear']])

position_size_bear = []

for index, row in data.iterrows():
    if row['entry_signal_bear'] == 1:
        amt_per_trade = equity * (risk_percent/100)
        position_size_bear.append(math.floor(amt_per_trade /row['close']))
    else:
        position_size_bear.append(0)
        
        
data['position_size_bear'] = position_size_bear
# print(position_size_bear)

position = 0
total_profit_bear = 0
entry_price = None
position_qty = 0

for i, row in data.iterrows():
    if row['exit_signal_bear'] == 1:
        if position != 0 and entry_price != None:
            exit_price = row['close']                      
            profit = (entry_price - exit_price) * position_qty #* position_qty #if position == 1 else (entry_price - exit_price)
            total_profit_bear += profit
            position = 0  # No position
            position_qty = 0
           
    if row['entry_signal_bear'] == 1:
        if position == 0:
            position = 1  
            entry_price = row['close']
            position_qty = row['position_size_bear']


print("total_profit_bear: " + str(total_profit_bear))

# print(data[['open_price', 'close', 'entry_signal_bear', 'exit_signal_bear']])
# print(data['exit_signal_bear'])


##--------##

# Create the candlestick plot
fig = go.Figure(data=[go.Candlestick(x=data['time'],
                                     open=data['open_price'],
                                     high=data['high'],
                                     low=data['low'],
                                     close=data['close'])])

# Add entry and exit signals for the bull positions
fig.add_trace(go.Scatter(x=data[data['entry_signal_bull'] == 1]['time'],
                         y=data[data['entry_signal_bull'] == 1]['close'] - 1.0,
                         mode='markers',
                         marker=dict(symbol='triangle-up', size=14),
                         name='BarUp'))

# Add entry and exit signals for the bear positions
fig.add_trace(go.Scatter(x=data[data['entry_signal_bear'] == 1]['time'],
                          y=data[data['entry_signal_bear'] == 1]['open_price'] + 1.0,
                          mode='markers',
                          marker=dict(symbol='arrow-bar-down', size=12),
                          name='BarDn'))


# Add text annotation below the chart
fig.add_annotation(
    x=data['time'][2],
    y=1.1,
    xref='x',
    yref='paper',
    text="Bull Profit: " + str(round(total_profit_bull,2)),
    showarrow=False,
    font=dict(color='black', size=15)
)

# Add text annotation below the chart
fig.add_annotation(
    x=data['time'][30],
    y=1.1,
    xref='x',
    yref='paper',
    text="Bear Profit: " + str(round(total_profit_bear,2)),
    showarrow=False,
    font=dict(color='black', size=15)
)

# Add text annotation below the chart
fig.add_annotation(
    x=data['time'][2],
    y=1.2,
    xref='x',
    yref='paper',
    text="Total Profit: " + str((round((total_profit_bear)+(total_profit_bull),2))),
    showarrow=False,
    font=dict(color='black', size=15)
)


# Set layout properties
fig.update_layout(title='SMA Candlestick Plot with Crossover & Crossunder',
                  title_x=0.5, 
                  xaxis_title='Time',
                  yaxis_title='Price',
                  legend_title='Signals',
                  xaxis_rangeslider_visible=False)

# Display the plot as an HTML file
offline.plot(fig, filename='sma_candlestick_plot.html')