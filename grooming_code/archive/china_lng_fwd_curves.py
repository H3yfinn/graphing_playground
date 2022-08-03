#%%
import pandas as pd
import numpy as np
import os

pd.options.plotting.backend = "plotly"#set pandas backend to plotly plotting instead of matplotlib

import plotly.io as pio

import plotly.graph_objects as go

#%%
#import data

Data_sort = pd.read_excel('../input_data/China spot LNG import price (1).xlsx', sheet_name='Data_sort')

#%%
#make Month the label for each curve
#then for each Label wqe ahve three dates with corrsponding prices which amkes the fwd curve
Data_sort['current_date'] = pd.to_datetime(Data_sort['Month'], format="%d/%m/%Y")

#%%
##TEMP
#make p+1 the price for the current month so we can seee how the graph looks with a current price. we will also remove p+1 as a datapoint in the price curves
Data_sort['current_price'] = Data_sort['p+1'].astype(float)

#%%

key, unique = pd.factorize(Data_sort['current_date'])
Data_sort['current_date_key'] = key

fwd_price_df = Data_sort.copy()[['p+1',	'p+2', 'p+3']] 
fwd_price_df['current_date_key'] = key

fwd_date_df = Data_sort.copy()[['m+1',	'm+2', 'm+3']]
fwd_date_df['current_date_key'] = key

#sort current_price_df so current_date is in order of early to last
current_price_df = Data_sort.copy()[['current_price', 'current_date']]
current_price_df.sort_values(by='current_date', inplace=True)

#%%
#serparate a dtf for each of (p+1, m+1), (p+2, m+2) etc. combinations with current_date as the index
Data_sort_0 = Data_sort[['current_date', 'current_date', 'current_price']]#we use fwd_period = 0 so that there is still a line connecting current price to the fwd_price price
Data_sort_1 = Data_sort[['current_date', 'm+1', 'p+1']]
Data_sort_2 = Data_sort[['current_date', 'm+2', 'p+2']]
Data_sort_3 = Data_sort[['current_date', 'm+3', 'p+3']]

#then create another column which is the extra month fwd_period, so. fwd_period = 1, 2 or 3
Data_sort_0['fwd_period'] = 0
# Data_sort_1['fwd_period'] = 1#add me when you remove TEMP
Data_sort_2['fwd_period'] = 2#add me when you remove TEMP
Data_sort_3['fwd_period'] = 3#add me when you remove TEMP

#now make the columns more clear:
Data_sort_0.columns.values[1] = 'fwd_date'
Data_sort_0.columns.values[2] = 'fwd_price'

Data_sort_1.rename(columns={'m+1': 'fwd_date', 'p+1': 'fwd_price'}, inplace=True)
Data_sort_2.rename(columns={'m+2': 'fwd_date', 'p+2': 'fwd_price'}, inplace=True)
Data_sort_3.rename(columns={'m+3': 'fwd_date', 'p+3': 'fwd_price'}, inplace=True)

#now concatenate
Data_sort_long = pd.concat([Data_sort_0,  Data_sort_2, Data_sort_3])#TEMP Data_sort_1,

#convert fwd_date to a datetime object
Data_sort_long['fwd_date'] = pd.to_datetime(Data_sort_long['fwd_date'], format="%d/%m/%Y")

#convert current_date to a unique value that wont be mnistaken as a datetime objet by plotly
key, unique = pd.factorize(Data_sort_long['current_date'])
Data_sort_long['current_date_key'] = key

#%%
##TEMP
#join current_price onto data_sort_long using current_date as key
Data_sort_long = Data_sort_long.merge(Data_sort[['current_date', 'current_price']], on='current_date', how='left')

#%%
#TEST
#probably want to make it so that the fwd_date is actually just X=fwd_period months ahead of the month it is in. this will make the data more interesting
# Data_sort_long['fwd_date'] = Data_sort_long['current_date'] + Data_sort_long['fwd_period'] #.apply(pd.offsets.Month)#note that pwd.Offsets doesnt do month probably because of how months can have any numbert of days in it# pd.DateOffset(months=
# df['C'] = df['A'] + df['B'].apply(pd.offsets.Day)
#%%
#Create plotting data structure now that we have all data we need

#change the shape of the df so we have a column for each fwd_period and a row for each new set of fwd_prices (or, current_date_key), and fill the cells with fwd prices. 
#Then associated with that we will have a separate, same shaped df but replace the fwd_prices with fwd_dates
#then we will also create a df with just the current price and current_month

fwd_price_df = Data_sort_long.copy()[['fwd_price', 'fwd_period', 'current_date_key']]
fwd_date_df = Data_sort_long.copy()[['fwd_date', 'fwd_period', 'current_date_key']]
current_price_df = Data_sort_long.copy()[['current_price', 'current_date','current_date_key']]

fwd_price_df = fwd_price_df.pivot_table(index='current_date_key', columns='fwd_period', values='fwd_price')
fwd_date_df = fwd_date_df.pivot_table(index='current_date_key', columns='fwd_period', values='fwd_date')

#sort current_price_df so current_date is in order of early to last
current_price_df = current_price_df.sort_values(by='current_date')


#%%


#%%
#plot the data using plotly. because of nature of this graph we will ahve to do it in a more complicated fashion

title = 'China LNG Forward Curves'

#plot
fig = go.Figure()
for row_i in range(len(fwd_price_df)):
    #plot each row of the df as a separate curve
    fig.add_trace(go.Scatter(x=fwd_date_df.iloc[row_i], y=fwd_price_df.iloc[row_i], mode='lines', opacity=0.3, line_color='#6fa0ed', showlegend=False,name='Forward Price'))

    if (row_i+1) == len(fwd_price_df):
        #add name for the legend
        fig.add_trace(go.Scatter(x=fwd_date_df.iloc[row_i], y=fwd_price_df.iloc[row_i], mode='lines', opacity=0.3, line_color='#6fa0ed', name='Forward Price'))

#plot current price
fig.add_trace(go.Scatter(x=current_price_df['current_date'], y=current_price_df['current_price'], mode='lines', opacity=1, line_color='#013a94', connectgaps=True, name="Current Price"))

#add titles
fig.update_layout(title='China LNG Forward Curves', xaxis_title='Date', yaxis_title='Price', xaxis_type='date')

#save. 
import plotly
plotly.offline.plot(fig, filename='../plotting_output/' + title + '.html', auto_open=False)
fig.write_image("../plotting_output/static/" + title + '.png')

# %%
