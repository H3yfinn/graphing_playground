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
##TEMP
#make p+1 the price for the current month so we can seee how the graph looks with a current price. we will also remove p+1 as a datapoint in the price curves
Data_sort['current_price'] = Data_sort['p+1'].astype(float)

#there is now a signifcant decision as to whether to make the price for m+1 the current price or the interpolated price between current price and m+2
#if we want the interpolated price, we will just remove the m+1 column. else we keep it. You will seee below:

#%%
#recreate the shape of the df so we have a column for each fwd_period and a row for each new set of fwd_prices (or, current_date_key), and fill the cells with fwd prices. 
#Then associated with that we will have a separate, same shaped df but replace the fwd_prices with fwd_dates
#then we will also create a df with just the current price and current_month

fwd_price_df = Data_sort.copy()[['current_price', 'p+1', 'p+2', 'p+3']] 

#remove p+1 from the df since we dont want it in the price curves
fwd_price_df = fwd_price_df.drop(columns=['p+1'])#comment this line out if you dont want interpolatedd price for m+1


fwd_date_df = Data_sort.copy()[['Month', 'm+1', 'm+2', 'm+3']]

#remove m+1 from the df since we dont want it in the price curves
fwd_date_df = fwd_date_df.drop(columns=['m+1'])#comment this line out if you dont want interpolatedd price for m+1


current_price_df = Data_sort.copy()[['current_price', 'Month']]
current_price_df.sort_values(by='Month', inplace=True)


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
fig.add_trace(go.Scatter(x=current_price_df['Month'], y=current_price_df['current_price'], mode='lines', opacity=1, line_color='#013a94', connectgaps=True, name="Current Price"))

#add titles
fig.update_layout(title='China LNG Forward Curves', xaxis_title='Date', yaxis_title='Price', xaxis_type='date')

#save. 
import plotly
plotly.offline.plot(fig, filename='../plotting_output/' + title + '.html', auto_open=False)
fig.write_image("../plotting_output/static/" + title + '.png')

# %%
