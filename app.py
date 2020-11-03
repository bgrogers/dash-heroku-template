#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
from datetime import date
import dash
#from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# In[2]:


ecv = pd.read_csv("https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/538%20Polling%20Averages/election_basics_10_26.csv", index_col=False)
ecv.columns
national = ecv[ecv['State'] == 'National']
national = national.drop(columns=['ECV', 'State','State_abb'])
ecv = ecv.drop(0)
ecv = ecv.sort_values('State')
ecv = ecv.reset_index(drop = True)


# In[3]:


national.head()


# In[4]:


ecv.head()


# In[5]:


ind_vote = pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/independent%20vote%20total.csv')
ind_count = np.mean(ind_vote['vote_ind'])/100


# # Economist

# In[6]:


election = pd.read_csv("https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/economist_model_output/10_26/state_averages_and_predictions_topline.csv",index_col=False)
election.columns

election = election.sort_values('state')
election.head(5)


# In[7]:


econ_df = pd.concat([ecv, election], axis=1, sort=False, join='inner')


# In[8]:


econ_df.head()


# In[9]:


econ_df['result'] = pd.cut(econ_df.projected_win_prob, [-1, 0.5, 1], labels=['Donald Trump','Joe Biden'])
econ_df['State Rating'] = pd.cut(econ_df.projected_win_prob, [-.0001, .25,.4, .5 ,.6,.75,1.1], labels=['Safe R', 'Likely R','Slightly R','Slightly D','Likely D','Safe D'])
econ_df.head(50)


# In[10]:


econ_df.columns


# In[11]:


Trump_ECV = econ_df.query("result == 'Donald Trump'")['ECV'].sum()
Biden_ECV = econ_df.query("result == 'Joe Biden'")['ECV'].sum()
print('Joe Biden: ',Biden_ECV,' Donald Trump: ',Trump_ECV )


# In[12]:


econ_map = px.choropleth(econ_df, locations='State_abb', 
                    hover_name='State', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
econ_map.add_trace(go.Scattergeo(locations = econ_df['State_abb'],
                  locationmode = 'USA-states',
                  text = econ_df['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


econ_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
econ_map.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     geo_bgcolor="#F5F5F5",title={'text': "</b>Economist Model Result:</b> Biden: 334  Trump: 204",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
econ_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# # Time for Change

# In[13]:


trump_pred=38.1494
trump_current = national['Polls_Trump_10_26_538'].iloc[0]
trumppollschange = trump_current-trump_pred
tfcnational = national.copy()
tfcnational['Polls_Biden_10_26_538'] = tfcnational['Polls_Biden_10_26_538']+trumppollschange
tfcnational['Polls_Trump_10_26_538'] = tfcnational['Polls_Trump_10_26_538']-trumppollschange
tfcnational['Biden_adj'] = 100-tfcnational['Polls_Trump_10_26_538']-ind_count
tfc = ecv.copy()
tfc['Polls_Biden_10_26_538'] = tfc['Polls_Biden_10_26_538']+trumppollschange
tfc['Polls_Trump_10_26_538'] = tfc['Polls_Trump_10_26_538']-trumppollschange
tfc['Biden_adj'] =100-tfc['Polls_Trump_10_26_538']-ind_count
tfc.head()


# In[14]:


tfc['difference'] = tfc['Polls_Trump_10_26_538'] - tfc['Polls_Biden_10_26_538']
tfc['dif_adj'] = tfc['Polls_Trump_10_26_538'] - tfc['Biden_adj']
tfc['result'] = pd.cut(tfc.difference, [-120, -.000001,0,120], labels=['Joe Biden','Tie','Donald Trump'])
tfc['result_adj'] = pd.cut(tfc.dif_adj, [-120, -.000001,0,120], labels=['Joe Biden','Tie','Donald Trump'])
tfc['State Rating'] = pd.cut(tfc.difference, [-120, -20,-5, 0 ,5,20,120], labels=['Safe D', 'Likely D','Slightly D','Slightly R','Likely R','Safe R'])
tfc['State Rating adj'] = pd.cut(tfc.dif_adj, [-120, -20,-5, 0 ,5,20,120], labels=['Safe D', 'Likely D','Slightly D','Slightly R','Likely R','Safe R'])
tfc.head()


# In[15]:


tfc_trump = tfc.query("result == 'Donald Trump'")['ECV'].sum()
tfc_biden = tfc.query("result == 'Joe Biden'")['ECV'].sum()
tfc_trump_adj = tfc.query("result_adj == 'Donald Trump'")['ECV'].sum()
tfc_biden_adj = tfc.query("result_adj == 'Joe Biden'")['ECV'].sum()


# In[16]:


print('Biden',tfc_biden_adj,'Trump',tfc_trump_adj)


# In[17]:


tfc_map = px.choropleth(tfc, locations='State_abb', 
                    hover_name='State', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating adj', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating adj": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
tfc_map.add_trace(go.Scattergeo(locations = tfc['State_abb'],
                  locationmode = 'USA-states',
                  text = tfc['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


tfc_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
tfc_map.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     geo_bgcolor="#F5F5F5",title={'text': "</b>Time for Change with State Polls Result:</b> Biden: 479 Trump: 59",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
tfc_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# # Twitter Model

# In[18]:


trump_pred=45.82462436098755
trump_current = national['Polls_Trump_10_26_538'].iloc[0]
tmpc = trump_current - trump_pred
tmnational = national.copy()
tmnational['Polls_Biden_10_26_538'] = tmnational['Polls_Biden_10_26_538']+tmpc
tmnational['Polls_Trump_10_26_538'] = tmnational['Polls_Trump_10_26_538']-tmpc
tmnational['Biden_adj'] = 100 - tmnational['Polls_Trump_10_26_538']-ind_count
tm = ecv.copy()
tm['Polls_Biden_10_26_538'] = tm['Polls_Biden_10_26_538']+tmpc
tm['Polls_Trump_10_26_538'] = tm['Polls_Trump_10_26_538']-tmpc
tm['Biden_adj'] = 100 - tm['Polls_Trump_10_26_538']-2.7
tm.head()


# In[19]:


tm['difference'] = tm['Polls_Trump_10_26_538'] - tm['Polls_Biden_10_26_538']
tm['dif_adj'] = tm['Polls_Trump_10_26_538'] - tm['Biden_adj']
tm['result'] = pd.cut(tm.difference, [-120, -.00001, 0, 120], labels=['Joe Biden','tie','Donald Trump'])
tm['result_adj'] = pd.cut(tm.dif_adj, [-120, -.00001, 0, 120], labels=['Joe Biden','tie','Donald Trump'])
tm['State Rating'] = pd.cut(tm.difference, [-120, -20,-5, 0 ,5,20,120], labels=['Safe D', 'Likely D','Slightly D','Slightly R','Likely R','Safe R'])
tm['State Rating adj'] = pd.cut(tm.dif_adj, [-120, -20,-5, 0 ,5,20,120], labels=['Safe D', 'Likely D','Slightly D','Slightly R','Likely R','Safe R'])

tm.head()


# In[20]:


tm


# In[21]:


tm_trump = tm.query("result == 'Donald Trump'")['ECV'].sum()
tm_biden = tm.query("result == 'Joe Biden'")['ECV'].sum()
tm_trump_adj = tm.query("result_adj == 'Donald Trump'")['ECV'].sum()
tm_biden_adj = tm.query("result_adj == 'Joe Biden'")['ECV'].sum()
print('Trump:',tm_trump,'Biden: ',tm_biden,'Tadj',tm_trump_adj, 'Badj',tm_biden_adj)


# In[22]:


tm_show = tm[['State','State_abb','ECV','Polls_Trump_10_26_538','Biden_adj','dif_adj','State Rating adj']]


# In[23]:


tm_show = tm_show.rename(columns={'Polls_Trump_10_26_538':'Trump', 'Biden_adj': 'Biden', 'dif_adj':'dif','State Rating adj': 'State Rating'})


# In[24]:


tm_map = px.choropleth(tm, locations='State_abb', 
                    hover_name='State', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
tm_map.add_trace(go.Scattergeo(locations = tm['State_abb'],
                  locationmode = 'USA-states',
                  text = tm['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


tm_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
tm_map.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     geo_bgcolor="#F5F5F5",title={'text': "</b>Twitter Model with State Polls Result:</b> Biden: 227 Trump: 311",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
tm_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# In[25]:


tm_map_adj = px.choropleth(tm, locations='State_abb', 
                    hover_name='State', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating adj', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
tm_map_adj.add_trace(go.Scattergeo(locations = tm['State_abb'],
                  locationmode = 'USA-states',
                  text = tm['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


tm_map_adj.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
tm_map_adj.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     geo_bgcolor="#F5F5F5",title={'text': "</b>Twitter Model with State Polls Result:</b> Biden: 279 Trump: 259 ",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
tm_map_adj.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# # Fair Vote Equation

# In[26]:


trump_pred=49.40298000000001
trump_current = national['Polls_Trump_10_26_538'].iloc[0]
trumppollschange = trump_current - trump_pred
fvenational = national.copy()
fvenational['Polls_Biden_10_26_538'] = fvenational['Polls_Biden_10_26_538']+trumppollschange
fvenational['Polls_Trump_10_26_538'] = fvenational['Polls_Trump_10_26_538']-trumppollschange
fvenational['Biden_adj'] = 100 - fvenational['Polls_Trump_10_26_538']-ind_count
fve = ecv.copy()
fve['Polls_Biden_10_26_538'] = fve['Polls_Biden_10_26_538']+trumppollschange
fve['Polls_Trump_10_26_538'] = fve['Polls_Trump_10_26_538']-trumppollschange
fve['Biden_adj'] = 100 - fve['Polls_Trump_10_26_538']-ind_count
fve.head()


# In[27]:


fve['difference'] = fve['Polls_Trump_10_26_538'] - fve['Polls_Biden_10_26_538']
fve['dif_adj'] = fve['Polls_Trump_10_26_538'] - fve['Biden_adj']
fve['result'] = pd.cut(fve.difference, [-120, -.00001, 0, 120], labels=['Joe Biden','tie','Donald Trump'])
fve['result_adj'] = pd.cut(fve.dif_adj, [-120, -.00001, 0, 120], labels=['Joe Biden','tie','Donald Trump'])
fve['State Rating'] = pd.cut(fve.difference, [-120, -20,-5, 0 ,5,20,120], labels=['Safe D', 'Likely D','Slightly D','Slightly R','Likely R','Safe R'])
fve['State Rating adj'] = pd.cut(fve.dif_adj, [-120, -20,-5, 0 ,5,20,120], labels=['Safe D', 'Likely D','Slightly D','Slightly R','Likely R','Safe R'])
fve.head()


# In[28]:


fve_trump = fve.query("result == 'Donald Trump'")['ECV'].sum()
fve_biden = fve.query("result == 'Joe Biden'")['ECV'].sum()
fve_trump_adj = fve.query("result_adj == 'Donald Trump'")['ECV'].sum()
fve_biden_adj = fve.query("result_adj == 'Joe Biden'")['ECV'].sum()
print('Trump:',fve_trump,'Biden: ',fve_biden,'Tadj',fve_trump_adj, 'Badj',fve_biden_adj)


# In[29]:


fve_map = px.choropleth(fve, locations='State_abb', 
                    hover_name='State', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating adj', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating adj": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
fve_map.add_trace(go.Scattergeo(locations = fve['State_abb'],
                  locationmode = 'USA-states',
                  text = fve['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


fve_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
fve_map.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#FEFDFD",
                     geo_bgcolor="#FEFDFD",title={'text': "</b>Fair Vote Equation with State Polls Result:</b> Biden: 227 Trump: 311",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
fve_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# # JHK

# In[30]:


jhk = pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/JHK%20Forecasts%20results/jhk_10_18.csv',index_col=False)
jhk.columns

jhk.head(5)


# In[31]:


jhk['difference'] = jhk['jhk_biden'] - jhk['jhk_trump']
jhk['result'] = pd.cut(jhk.difference, [-100, 0, 100], labels=['Donald Trump','Joe Biden'])
jhk['State Rating'] = pd.cut(jhk.difference, [-100, -5,-2, 0 ,2,5,100], labels=['Safe R', 'Likely R','Slightly R','Slightly D','Likely D','Safe D'])
jhk = jhk.iloc[1:]
jhk


# In[32]:


Trump_ECV = jhk.query("result == 'Donald Trump'")['ECV'].sum()
Biden_ECV = jhk.query("result == 'Joe Biden'")['ECV'].sum()
print('Joe Biden: ',Biden_ECV,' Donald Trump: ',Trump_ECV )


# In[33]:


jhk_map = px.choropleth(jhk, locations='State_abb', 
                    hover_name='State', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
jhk_map.add_trace(go.Scattergeo(locations = jhk['State_abb'],
                  locationmode = 'USA-states',
                  text = jhk['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


jhk_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
jhk_map.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     geo_bgcolor="#F5F5F5",title={'text': "</b>JHK Forecasting Result:</b> Biden: 356 Trump: 182",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
jhk_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# # PEC

# In[34]:


pec = pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/PEC%20results/PEC%2010_19.csv',index_col=False)
pec.columns

pec.head(5)


# In[35]:



pec['result'] = pd.cut(pec.trump_lead, [-100, 0, 100], labels=['Joe Biden','Donald Trump'])
pec['State Rating'] = pd.cut(pec.trump_lead, [-100, -2,-1, 0 ,1,2,100], labels=['Safe D', 'Likely D','Slightly D','Slightly R','Likely R','Safe R'])
pec.head()


# In[36]:


Trump_ECV = pec.query("result == 'Donald Trump'")['ECV'].sum()
Biden_ECV = pec.query("result == 'Joe Biden'")['ECV'].sum()
print('Joe Biden: ',Biden_ECV,' Donald Trump: ',Trump_ECV )


# In[37]:


pec_map = px.choropleth(pec, locations='State_abb', 
                    hover_name='State', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
pec_map.add_trace(go.Scattergeo(locations = pec['State_abb'],
                  locationmode = 'USA-states',
                  text = pec['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


pec_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
pec_map.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#FEFDFD",
                     geo_bgcolor="#FEFDFD",title={'text': "</b>Princeton Election Consortium:</b> Biden: 356 Trump: 182",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
pec_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# # Plural Vote

# In[38]:


pv = pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/Plural%20Vote%20Results/plural_vote_10_7.csv',index_col=False)
pv.columns

pv.head(5)


# In[39]:


pv['difference'] = pv['biden_est'] - pv['trump_est']
pv['result'] = pd.cut(pv.difference, [-100, 0, 100], labels=['Donald Trump','Joe Biden'])
pv['State Rating'] = pd.cut(pv.difference, [-100, -2,-1, 0 ,1,2,100], labels=['Safe R', 'Likely R','Slightly R','Slightly D','Likely D','Safe D'])
pv.head()


# In[40]:


Trump_ECV = pv.query("result == 'Donald Trump'")['ecv'].sum()
Biden_ECV = pv.query("result == 'Joe Biden'")['ecv'].sum()
print('Joe Biden: ',Biden_ECV,' Donald Trump: ',Trump_ECV )


# In[41]:


pv_map = px.choropleth(pv, locations='state_abb', 
                    hover_name='state', hover_data = {'ecv' : True , "state_abb" : False},
                    locationmode='USA-states', color='State Rating', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
pv_map.add_trace(go.Scattergeo(locations = pv['state_abb'],
                  locationmode = 'USA-states',
                  text = pv['ecv'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


pv_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
pv_map.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#FEFDFD",
                     geo_bgcolor="#FEFDFD",title={'text': "</b>Plural Vote:</b> Biden: 345 Trump: 193",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
pv_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})
   


#  ## Bayesian Model

# In[42]:


BaM = pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/Bayesian_model/results_bayesian_model.csv',index_col=False)
BaM.columns

BaM.head(5)


# In[43]:


BaM['difference'] = BaM['dem'] - BaM['rep']
BaM['result'] = pd.cut(BaM.difference, [-1, 0, 1], labels=['Donald Trump','Joe Biden'])
BaM['State Rating'] = pd.cut(BaM.difference, [-1, -.02,-.01, 0 ,.1,.2,1], labels=['Safe R', 'Likely R','Slightly R','Slightly D','Likely D','Safe D'])
BaM.head()


# In[44]:


Trump_ECV = BaM.query("result == 'Donald Trump'")['ECV'].sum()
Biden_ECV = BaM.query("result == 'Joe Biden'")['ECV'].sum()
print('Joe Biden: ',Biden_ECV,' Donald Trump: ',Trump_ECV )


# In[45]:


BaM_map = px.choropleth(BaM, locations='State_abb', 
                    hover_name='State', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
BaM_map.add_trace(go.Scattergeo(locations = fve['State_abb'],
                  locationmode = 'USA-states',
                  text = BaM['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


BaM_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
BaM_map.update_layout(autosize=False,width=1300,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     geo_bgcolor="#F5F5F5",title={'text': "</b>Bayesian Model with State Polls Result:</b> Biden: 395 Trump: 143",'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="black"),
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

             
   
   
BaM_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# # 538 Polls

# In[46]:


fte = pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/538%20Polling%20Averages/presidential_poll_averages_10_6.csv',index_col=False)

fte.columns


fte.head(5)


# In[47]:


fte['difference'] = fte['pct_estimate_biden'] - fte['pct_estimate_biden']
fte['result'] = pd.cut(BaM.difference, [-100, 0, 100], labels=['Donald Trump','Joe Biden'])
Trump_ECV = fte.query("result == 'Donald Trump'")['ecv'].sum()
Biden_ECV = fte.query("result == 'Joe Biden'")['ecv'].sum()
print('Joe Biden: ',Biden_ECV,' Donald Trump: ',Trump_ECV )


# In[48]:


polls_map = px.choropleth(fte, locations='state_abb', 
                    hover_name='state', hover_data = ['ecv'],
                    locationmode='USA-states', color='result', scope="usa",
                    
                    color_discrete_map = {'Joe Biden': px.colors.qualitative.Set1[1],  
                                         'Donald Trump':px.colors.qualitative.Set1[0]},
                       title = ('Bayesian Model: Biden 390 Trump: 148'))
polls_map.show()


# ## CTWH Model

# In[49]:



fundamental_probs = pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/notebooks/fundamentals_probs1015.csv')
poll_probs = pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/notebooks/poll_probs_11_3.csv')
codes=pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/notebooks/state_codes.csv')


# In[50]:


poll_probs.head()


# In[51]:


states = fundamental_probs.iloc[:, 1]

fundamental_probs = fundamental_probs.iloc[:, 0].values
dem_polls = poll_probs.loc[:, 'dem_prob'].values


today = date.today()
election_day = date(2020, 11, 3)
time_delta = (election_day - today).days

poll_proportion = .9 - time_delta * .01

final_probs = dem_polls * poll_proportion + fundamental_probs * (1 - poll_proportion)

ctwh_results = pd.DataFrame(index=states)
ctwh_results['Biden_Win_Probability'] = final_probs

#compute electoral votes based on probability of win over 0.5 for each state

electoral_votes = [9, 3, 11, 6, 55, 9, 7, 3, 3, 29, 16, 4, 4, 20, 11, 6, 6, 8, 8, 4,
10, 11, 16, 10, 6, 10, 3, 5, 6, 4, 14, 5, 29, 15, 3,18, 7,
7, 20, 4, 9, 3, 11, 38, 6, 3, 13, 12, 5, 10, 3]

ctwh_results['electoral_votes'] = electoral_votes


# In[52]:


ctwh_results=pd.merge(codes,ctwh_results, on = ['States'])
ctwh_results.head()


# In[53]:


ctwh_results['result'] = pd.cut(ctwh_results.Biden_Win_Probability, [0, 0.5, 1], labels=['Donald Trump','Joe Biden'])
ctwh_results['State Rating'] = pd.cut(ctwh_results.Biden_Win_Probability, [0,.175,.35, .5 ,.65,.825,1], labels=['Safe R', 'Likely R','Slightly R','Slightly D','Likely D','Safe D'])
ctwh_results.sort_values(by=['Biden_Win_Probability'], inplace=True)
ctwh_results.head()


# In[54]:


Trump_ECV = ctwh_results.query("result == 'Donald Trump'")['ECV'].sum()
Biden_ECV = ctwh_results.query("result == 'Joe Biden'")['ECV'].sum()
print( "TrumpECV  =  " + str(Trump_ECV) +"    Biden ECV =  " + str(Biden_ECV ))


# In[55]:


ctwh_map = px.choropleth(ctwh_results, locations='State_abb', 
                    hover_name='States', hover_data = {'ECV' : True , "State_abb" : False},
                    locationmode='USA-states', color='State Rating', scope="usa",
                    color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"},   
                    category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", "Toss Up", "Slightly R", "Likely R", "Safe R"]})
                    
ctwh_map.add_trace(go.Scattergeo(locations = ctwh_results['State_abb'],
                  locationmode = 'USA-states',
                  text = ctwh_results['ECV'],
                  mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 13,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))


ctwh_map.update_traces(marker_line_width=0.2, marker_line_color = 'white')
                                 
ctwh_map.update_layout(autosize=False,width=1200,height=900, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     geo_bgcolor="#F5F5F5",
                     title={'text':'The Chase the White House Electoral Vote Total Prediction for 2020' +'<br>' +
                            'Joe Biden: ' + str(Biden_ECV) +   '           Donald Trump: ' + str(Trump_ECV), 
                            'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=32, color="rgb(33,102,172)"),
                     showlegend=True,
                     
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.7, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=18,color="black")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))
                   
   
config = dict({'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})    
ctwh_map.show(config=config)


# In[56]:

ctwh_bardata=ctwh_results.sort_values(by=['State Rating','ECV'], ascending=[True,False])
ctwh_bardata.head()


ctwh_bar = px.bar(ctwh_bardata, x="ECV", y='result' , color='State Rating', orientation='h',
             hover_data={'State_abb':False, 'result': False, 'States': True},
             height=300, width =1600,
             text = ctwh_bardata['State_abb'], 
             title= 'Predicted Electoral College Vote by State',
             #title='line1' + '<br>' +  '<span style="font-size: 18px;">line2</span>',
             labels=dict(result=" ", ECV="Total Electoral College Votes"),
             opacity=0.8,            
             category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D",  "Safe R", "Likely R", "Slightly R"]},
             color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                         "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"})
           
ctwh_bar.update_layout( margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     plot_bgcolor="#F5F5F5",
                     showlegend= False,
                     yaxis={'visible': False, 'showticklabels': True},
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

ctwh_bar.update_layout(shapes=[dict(type= 'line',
      yref= 'paper', y0= 0, y1= .8,
      xref= 'x', x0= 270, x1= 270,
      line=dict(color="Gray",width=5))])

ctwh_bar.add_annotation(x=270, y=2,
            text="270 to Win",
            showarrow=False,
               yshift=10           )

ctwh_bar.show()


# In[57]:


# Create Time Animated Map of Change Over Time
## Currently Mocked Up Placeholding Data
ctwh_change=pd.read_csv('https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/notebooks/updated_probs_11_3.csv')
ctwh_change.head()


# In[58]:


ctwh_change['result'] = pd.cut(ctwh_change.combine_probs, [0, 0.5, 1], labels=['Donald Trump','Joe Biden'])
ctwh_change['State Rating'] = pd.cut(ctwh_change.combine_probs, [0,.15,.35, .5 ,.65,.85,1], labels=['Safe R', 'Likely R','Slightly R','Slightly D','Likely D','Safe D'])
ctwh_change['timeframe']=ctwh_change['Days out from the Election']
ctwh_change.tail()


# In[59]:


Trump_ECV_10 = ctwh_change.query("result == 'Donald Trump' and timeframe == '10'")['ECV'].sum()
Biden_ECV_10 = ctwh_change.query("result == 'Joe Biden' and timeframe == '10'")['ECV'].sum()
Trump_ECV_20 = ctwh_change.query("result == 'Donald Trump' and timeframe == '20'")['ECV'].sum()
Biden_ECV_20 = ctwh_change.query("result == 'Joe Biden' and timeframe == '20'")['ECV'].sum()
Trump_ECV_30 = ctwh_change.query("result == 'Donald Trump' and timeframe == '30'")['ECV'].sum()
Biden_ECV_30 = ctwh_change.query("result == 'Joe Biden' and timeframe == '30'")['ECV'].sum()
Trump_ECV_40 = ctwh_change.query("result == 'Donald Trump' and timeframe == '40'")['ECV'].sum()
Biden_ECV_40 = ctwh_change.query("result == 'Joe Biden' and timeframe == '40'")['ECV'].sum()
Trump_ECV_50 = ctwh_change.query("result == 'Donald Trump' and timeframe == '50'")['ECV'].sum()
Biden_ECV_50 = ctwh_change.query("result == 'Joe Biden' and timeframe == '50'")['ECV'].sum()

print('50 days Out: Joe Biden: ',Biden_ECV_50,' Donald Trump: ',Trump_ECV_50 )
print('40 days Out: Joe Biden: ',Biden_ECV_40,' Donald Trump: ',Trump_ECV_40 )
print('30 days Out: Joe Biden: ',Biden_ECV_30,' Donald Trump: ',Trump_ECV_30 )
print('20 days Out: Joe Biden: ',Biden_ECV_20,' Donald Trump: ',Trump_ECV_20 )
print('10 days Out: Joe Biden: ',Biden_ECV_10,' Donald Trump: ',Trump_ECV_10 )


# In[60]:


ctwh_change_map = px.scatter_geo(ctwh_change, locationmode="USA-states", locations= 'State_abb',color="State Rating",
                     hover_name="State", size="ECV", size_max=36,
                      color_discrete_map={
                        "Safe D": "rgb(33,102,172)",
                        "Likely D": "rgb(67,147,195)",
                        "Slightly D": "rgb(146,197,222)",
                        "Slightly R": "rgb(239,59,44)",
                        "Likely R": "rgb(203,24,29)",
                        "Safe R": "rgb(165,15,21)"}, 
                     category_orders={"State Rating": ["Safe D", "Likely D", "Slightly D", 
                                                       "Toss Up", "Slightly R", "Likely R", "Safe R"]},
                     animation_frame="Days out from the Election",
                     projection="albers usa")
                    
ctwh_change_map.add_trace(go.Scattergeo(locations = ctwh_change['State_abb'],
                  locationmode = 'USA-states',
                  text = ctwh_change['ECV'],
                     mode = 'text', 
                  textfont_color = 'white',
                  textfont_size = 10,
                  hoverinfo='skip',
                  textposition= 'middle center',
                  showlegend=False))

ctwh_change_map.update_layout(autosize=False,width=1000,height=800, margin=dict( l=50,r=50,b=50,t=50, pad=4),paper_bgcolor="#F5F5F5",
                     geo_bgcolor="#F5F5F5",
                     
                     title={'text': "Change in the Chase the White House Model's Prediction", 
                            'y':0.9,'x':0.5,'xanchor': 'center', 'yanchor': 'top'},
                     title_font=dict(family="Tahoma",size=30, color="rgb(33,102,172)"),
                     legend=dict(title_font_family="Tahoma", yanchor='top', y=0.5, xanchor="right",x=0.99,
                                 font=dict(family="Tahoma", size=16, color="rgb(33,102,172)")),
                     hoverlabel=dict(bgcolor="white", font_size=12,font_family="Tahoma"))

ctwh_change_map.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1800


ctwh_change_map.show(config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})


# # Dash App

# ## TRUE SCRIPT

# In[61]:

#suppress_callback_exceptions=True

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

colors = {'background': '#F5F5F5', 'header': '#D54122'}


index_page = html.Div(style={'backgroundColor': colors['background']}, children=[
    
html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),
    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About US', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),
    
    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),
    
    html.Center(children = [  html.H1('Our Model 10/26')]),
    
    html.Center(children = [dcc.Graph(figure=ctwh_map,config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})]),    
        
    html.Br(),
    
    
    html.Center(children = [dcc.Graph(figure=ctwh_bar, config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})]),   

    html.Br(),
    
    html.Center(children = [dcc.Graph(figure=ctwh_bar, config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})]), 
    
    html.Br(),
    
    html.Center(children=[html.H2('Description of Chase the White House Model')]),
    html.Center(children=[dcc.Markdown('''
    Our model consists of two parts: a polling-based model and a ‘fundamentals’ model. The fundamentals-only model uses predictors such as demographics, economic data, and past election results.
    The final model blends the two by weighting them, with the polling model getting more weight as election day approaches. The idea is that the further away the election is, the less predictive the polls become. ''')]),
    
    html.Center(children=[dcc.Markdown(''' 
    To construct our fundamentals model, we collected data at both the state and national level. This data includes economic indicators such as per-capita income, past election results, 
    and demographic data taken from the U.S. Census. We started with approximately 30 predictors and used a lasso regression and a random forest to filter down to the best predictors. ''')]),
    
    html.Br(),
    html.Center(children = [html.H3('Clink the links below to visit the different pages for the Models we have studied')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Br(),
            html.Div( children = [
                dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
                dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
                dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
                dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
                dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
            html.Br(),
            html.Br(),
            html.Div( children = [
                dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
                dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
                dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
                dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
                dcc.Link('About US', href='/About_Us',)],
                style={ 'display': 'inline-block'}),
            html.Br()])]),
    html.Br(),
    html.Center(children = [html.H2('Our Code')]),
    html.Br(),
    html.Center(children = [dcc.Markdown('''
    All links above are to different models we have studied or recreated in our work predicting the Presidential election and offer a wide variety of methods of forecasting. All credit goes to the creators of those models.
    All of our code can be found on our Github page linked below. Some models have their Github code linked on the page itself. All models we selected we picked because they share their code. There are other famous models out there,
    but since they do not share their code we will not be referencing their models. Our Github page is [https://github.com/bgrogers/ChaseTheWhiteHouse/](https://github.com/bgrogers/ChaseTheWhiteHouse/).
    
    ''')]),  
    html.Br(),
    html.Center(children=[
        html.Div(children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'25%', 'width':'25%','marginRight':10,'marginBottom':0})],href='https://github.com/bgrogers/ChaseTheWhiteHouse/'),
           
    ])]),
    html.Br(),                       
    html.Center(children=[html.H2('Links to Creators sources')]),
    html.Br(),    
    html.Center(children= [
        html.H3('The Economist'),
        dcc.Markdown('''Economist Model Model by G. Elliot Morris Twitter: @gelliotmorris'''), 
        dcc.Markdown('''Economist repository: https://github.com/TheEconomist/us-potus-model'''), 
        dcc.Markdown('''Economist Presidential Election website: https://projects.economist.com/us-2020-forecast/president'''),
        html.Br(),
        html.H3('Sabato\'s Crystall Ball'),
        dcc.Markdown('''Sabato's Crystall Ball by Larry Sabato Twitter: @LarrySabato'''),
        dcc.Markdown('''Sabato's Crystall Ball website: https://centerforpolitics.org/crystalball/'''),
        html.Br(),
        html.H3('Princeton Election Consortium'),
        dcc.Markdown('''Princeton Election Consortium Model Model by Dr. Sam Wang Twitter: @SamWangPhD'''),
        dcc.Markdown('''Princeton Election Consortium repository code in Matlab: https://github.com/Princeton-Election-Consortium/data-backend'''), 
        dcc.Markdown('''Princeton Election Consortium Website: https://election.princeton.edu/category/2020-election/'''),
        html.Br(),
        html.H3('JHKForecasts'),
        dcc.Markdown('''JHKForecasts Model Model by Jack Kersting Twitter: @JHKersting JHKForecasts'''), 
        dcc.Markdown('''Repositroy code in JavaScript: https://github.com/bgrogers/jhkforecasts/tree/master/presidential-forecast'''), 
        dcc.Markdown('''JHKForecasts Website: https://projects.jhkforecasts.com/presidential-forecast/'''),
        html.Br(),
        html.H3('Plural Vote'),
        dcc.Markdown('''Plural Vote Model Model by Sean Le Van Twitter: @Plural_vote'''),
        dcc.Markdown('''Plural Vote repository code in R: https://github.com/seanelevan/Plural-Vote'''),
        dcc.Markdown('''Plural Vote Website: http://www.pluralvote.com/article/2020-forecast/'''),    
    ]),

    
    html.Center(children=[
    html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopata, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Sciene. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])
])
    


Economist_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),

    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Back to the Main Page', href='/', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About US', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),
    
    html.Br(),
    
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),
    
    html.Center(children=[html.H1('Economist Model')]),
    html.Center(children=[html.H2('Map on 10/26')]),
    dcc.Graph(figure=econ_map),
    html.Br(),
    html.Center(children=[dcc.Markdown('''The Economist Model is created by G. Elliot Morris, and others working at the Economist with assistance from Andrew Gelman and Merlin Heidemanns from Columbia University.
    The model has multiple layers, but it is based on fundamentals and polling and overall is a Bayesain model. The fundamental model was fit on each Presidential election from 1948 to 2016. 
    The team at the Economist uses such factors as state partisan shifts as well as correcting for biases in polling such as "partisan non-response bias".
    Each state has a polling rating affected by changes in similar states both geographically, how they voted in 2016, racial makeup, education level, median age, white evangelical Christian rating, and the population density.
    From there, the model is calculated similar to a model published by Drew Linzer. It uses Markov Chain Monte Carlo simulations allowing a random walk of the model to based on the prior created by the fundamentals and polling.
    20,000 simulations are done daily. For a more in-depth breakdown of the model, please visit https://projects.economist.com/us-2020-forecast/president/how-this-works or take a look at their model on the Economist website.
    You can click on the logo below to go to the page.''')]),
    
    html.Center(children=[html.A([
            html.Img(
                src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/The_Economist_Logo.png', 
        style={'height':'25%', 'width':'25%'})
    ], href='https://projects.economist.com/us-2020-forecast/president')]),
    html.Div(id='Economist'),
    
    html.Br(),
    html.Center(children = [dcc.Link('Go back to our Main Page', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopata, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Science. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])


tfc_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),
    
    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Back to the Main Page', href='/',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About US', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),

    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),

    html.Center(children=[html.H1('Time for Change')]),
    
    html.Div(id='Time for Change'),
    html.Center(children=[html.H2('Map on 10/26')]),
    
    html.Center(children=[dcc.Graph(figure =tfc_map, config={'scrollZoom': False,'displayModeBar': False, 'staticPlot': True})]),
    
    html.Center(children = [dcc.Markdown('''
    Time for Change is a model created by Professor Alan Abramowitz of Emory and is one of the most famous Fundamental Models. The model was first created in 1988.
    The model makes its prediction based on only three inputs: the growth rate of the economy during the second quarter of the election year, the incumbent president’s approval rating at mid-year,
    and the length of time the incumbent president’s party has controlled the White House. The last of these is what Abramowitz dubbed the ‘Time-for-change-factor’, arguing that the longer a 
    political party controls the presidency, the more likely the other party will be to win it back. To read more about the model, go to his most recent Academic Paper on the Time for Change Model 
    "It’s the Pandemic, Stupid! A Simplified Model for Forecasting the 2020 Presidential Election" by Alan Abramowitz at https://doi.org/10.1017/S1049096520001389
    
    Time For Change predicted Donald Trump would win in 2016 as Donald Trump won but had a lower national vote share. Since the model predicts the national vote share, it was technically incorrect but predicted the correct winner. 
    
    Vote equation
    The model’s vote equation reads as:

    V = A + 0.108 NETAPP + 0.543 Q2GDP + 4.313 TERM1INC

    Variable description
    Static Variables for 2020

    N = NETAPP Incumbent president’s net approval rating (approval-dis-approval) in the final Gallup Poll in June: -19

    G = Q2GDP Annualized growth rate of real GDP in the second quarter of the election year: -20

    T = TERM1INC Presence (1) or absence (0) of a first-term incumbent in the race: 1

    A = CONSTANT for 2020

    V = Incumbent share of the two-party presidential vote
    
    However, there was an update to the model, now the Plus 2 Terms Version of the Time for Change Model, meaning the new model is below.
    
    IVS = 51.32 + 0.5546*Q2GDP + 0.1094*JNA -3.99945*I2TIVS
    
    IVS = 51.32 + 0.5546*(-20) + 0.1094*(-19) -3.99945*(1)
    
    The result is that the Incumbend Vote Share for the 2020 presidential election is predicted to be 38.1494.
    
    
    To apply this national vote percentage to each state, we used state polling averages. This is the same polling method used with our other models that predict the National Vote total of incumbents. 
    We use [538's Polling Averages](https://projects.fivethirtyeight.com/polls/president-general/national/) as our base polls for the state. 538 calculates each state's current polling by 
    averaging polls available based on grades assigned by 538 for the pollster. This data is made publically available by 538. We calculate the difference between 538's polling average incumbent vote 
    and our predicted vote and apply this difference to all the states. As an example, if a candidate has 40% of the vote nationally, but our model predicts that they will receive 50% of the vote, we will add 10% to 538's polling average for each state.
    
    Code for our model can be found on our Github page. Click on the Github logo below to go there.
    ''')]),

    html.Center(children=[
        html.Div(children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'25%', 'width':'25%','marginRight':10,'marginBottom':0})],href='https://github.com/bgrogers/ChaseTheWhiteHouse/'),
           
    ])]),   
    html.Br(),
    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopata, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Science. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])


fve_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),
    
    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Back to our Main Page', href='/',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About US', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),
    
    html.Br(),
    
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),
    html.Br(),

    html.Center(children=[html.H1('Fair Vote Equation')]),
    html.Div(id='Fair Vote Equation'),
    html.Center(children=[html.H2('Map on 10/26')]),
    html.Center(children=[dcc.Graph(figure=fve_map)]),
    html.Br(),
    html.Center(children=[html.H3('Methodology')]),
    html.Center(children=[
            dcc.Markdown(''' 
            
            Fair Vote Equation is a fundamental based linear regression model developed by Dr. Ray Fair. 
            
            Fair - VOTE EQUATION MODEL 2020
            The equation to predict the 2020 presidential election is V = 48.06 + 0.673 (GI) – 0.721 (PI) + 0.792 (Z*I) + 2.25 (DPER) – 3.76 (DUR) + 0.21 (I) + 3.25 (WAR)
            
            Variable Description
            G = Growth rate of real per capita GDP in the first three quarters of the on-term election year (annual rate)
            P = absolute value of the growth rate of the GDP deflator in the first 15 quarters of the administration (annual rate) except for 1920, 1944, and 1948, where the values are zero.
            Z = Number of quarters in the first 15 quarters of the administration in which the growth rate of real per capita GDP is greater than 3.2 percent at an annual rate except for 1920, 1944, and 1948, where the values are zero
            I = 1 if there is a Democratic presidential incumbent at the time of the election and -1 if there is a Republican presidential incumbent
            DPER = 1 if a Democratic presidential incumbent is running again, -1 if a Republican presidential incumbent is running again, and 0 otherwise
            DUR = 0 if either party has been in the White House for one term, 1 [-1] if the Democratic [Republican] party has been in the White House for two consecutive terms, 1.25 [-1.25] if the Democratic [Republican] party has been in the White House for three consecutive terms, 1.50 [-1.50] if the Democratic [Republican] party has been in the White House for four consecutive terms, and so on
            WAR = 1 for the elections of 1918, 1920, 1942, 1944, 1946, and 1948, and 0 otherwise
            VP = Democratic share of the two-party presidential vote
            
            The incumbent's predicted Vote Share is 49.40298000000001 for 2020
            
            Fair Disclaimer from Dr. Ray Fair
            I did not make an economic forecast with my US model this time because the model has nothing to say about the effects of pandemics. I could try to subjectively constant adjust the estimated equations, but this would only be guessing. So I am going to let the user decide what values of G and P to use. The per capita growth rate in the first quarter of 2020 was -5.2 percent at an annual rate. 
            If your guess (annual rates) is -10 percent in the second quarter and -5 percent in the third quarter, then G is (1-.052)(1-.10)(1-.05) raised to the 1/3 power and then subtract 1, which is -6.76 percent. If you use the link "Compute your own prediction," this is done for you, where you need to give as inputs the per capita growth rates at annual rates for the second and third quarters. 
            The value of P through the first quarter of 2020 is 1.9 percent, so using 1.9 will likely be fairly close to the actual. Also note when choosing your estimates of per capita growth rates that population is growing at about 0.5 percent per year at an annual rate. So subtract 0.5 from estimates of non per capita growth rates.
            
            To apply this national vote percentage to each state, we used state polling averages. This is the same polling method used with our other models that predict the National Vote total of incumbents. 
            We use [538's Polling Averages](https://projects.fivethirtyeight.com/polls/president-general/national/) as our base polls for the state. 538 calculates each state's current polling by 
            averaging polls available based on grades assigned by 538 for the pollster. This data is made publically available by 538. We calculate the difference between 538's polling average incumbent vote 
            and our predicted vote and apply this difference to all the states. As an example, if a candidate has 40% of the vote nationally, but our model predicts that they will receive 50% of the vote, we will add 10% to 538's polling average for each state.
            

            ''')]),  
    
    html.Br(),
    html.Center(children=[
            dcc.Markdown(''' Click the link below to access our Time for Change model code on Github.
            ''')]),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgwrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://github.com/bgrogers/ChaseTheWhiteHouse/tree/master/TimeForAChange')])]),
    html.Br(),
    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopata, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Science. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])



bayesian_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
   html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),

    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Back to our Main Page', href='/',style={'marginRight': 30}),
            dcc.Link('About Us', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),
    
    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),
    
    html.Br(),

    html.Center(children=[html.H1('Bayesian Model')]),

    html.Center(children=[html.H2('Map on 10/5')]),
    html.Center(children=[dcc.Graph(figure=BaM_map)]),
    
    html.Br(),
    html.Center(children=[
            dcc.Markdown(''' Click the link below to access the Chase the White House Github Page.
            ''')]),
    html.Center(children=[
        html.Div(children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'25%', 'width':'25%','marginRight':10,'marginBottom':0})],href='https://github.com/bgrogers/ChaseTheWhiteHouse/'),])]),

    
    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopata, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Science. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])


sabato_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
   html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),


    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Back to our Main Page', href='/', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About Us', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),

    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),
    html.Br(),
    
    html.Center(children=[html.H1('Sabato\'s Crystal Ball')]),
    dcc.Markdown('''Sabato\'s Crystall Ball is run by the University of Virginia Center for Politics and is edited by
    Larry J. Sabato, Kyle Kondik, and J. Miles Coleman. They provide expert opinions on the Presidential, Senate, and House
    races looking at a variety of resources to form their insights. Sabato's Crystal Ball is the gold standard of 
    predicting election outcomes. To Visit Sabato's Crystall Ball click on the map below.'''),
   
    html.Center(children=[html.H2('Map on 10/8')]),
    html.Br(),
    html.Center(children=[html.A([
            html.Img(
                src="https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/Sabato's%20Crystal%20Ball/Sabato_10_8.png", 
        style={'display': 'flex','align-item': 'center', 'justify-content': 'center'})
    ], href='https://centerforpolitics.org/crystalball/')]),
    html.Br(),
    
    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopata, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Science. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])


pec_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
   html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),


    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Back to Our Main Page', href='/', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About US', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),

    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),

    html.Center(children=[html.H1('Princeton Election Consortium')]),
    
    html.Div(id='PEC'),
    html.Center(children=[html.H2('Map on 10/26')]),
    html.Center(children=[dcc.Graph(figure=pec_map)]),
    html.Br(),
    html.Center(children=[html.H3('Methodology')]),
    html.Center(children=[
            dcc.Markdown(''' 
            Princeton Election Consortium, (PEC), is a model created and run Princeton Professor Sam Wang since 2004. The website for this model is [https://election.princeton.edu/category/2020-election/](https://election.princeton.edu/category/2020-election/)  This model is updated daily.
            
            PEC is an entirely polling based model. It starts by calculating the median and estimated standard error of the mean. These are converted a z-score and the last 3 polls
            or polls within the last 7 days. The probability is calculated using a t-distribution.
            
            The probability distribution is calculated by finding the exact probability distribution. 
            
            Polls are unfiltered in this model. Because of there being organizations that produce outliers consistantly, the median is used to limit their impact. If there is a bias in the polling, this will affect the prediction of this model.
            An example of this comes in 2016. 2016 polling largely failed to account for the differences education when polling, imfamously leading to larger than average polling errors.
            Because of the polling bias, PEC incorrectly predicted Clinton to win. 
            ''')]),
    html.Br(),
    html.Center(children=[
            dcc.Markdown(''' Click the logo below to go to the Princeton Election Consortium Github to download their code.
            ''')]),
    html.Br(),
    html.Center(children=[
        html.Div(children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'25%', 'width':'25%','marginRight':10,'marginBottom':0})],href='https://github.com/Princeton-Election-Consortium/data-backend'),])]),

    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopta, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Science. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])



pv_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
   html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Back to our Main Page', href='/', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About US', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),

    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),
    
    html.Br(),


    html.Center(children=[html.H1('Plural Vote')]),
    html.Br(),
    html.Center(children=[html.H2('Map on 10/26')]),
    html.Center(children=[dcc.Graph(figure=pv_map)]),
    html.Br(),
    html.Center(children=[html.H3('Methodology')]),
    html.Center(children=[
            dcc.Markdown(''' 
            Plural Vote is a model created and run by Sean le Van. You can follow Plural Vote on Twitter at @plural_vote for regular updates. This model is updated daily.
            
            The model has two parts, polling and Google Search Trends of the candidates. The polling section is weighted to be 2/3rds of the output with the Google Search Trends constituting the other 3rd.
            The Search Trend model tracks shifts in the relative frequency of searches for Fox News, Washington Post, MSNBC, New York Times, and Huffington Post in each State. The Google Trend API can be found [here](https://trends.google.com/trends/?geo=US).
            This model is used to account for the media polarization. For more information on this section of the mode visit [Plural Vote's Website](https://www.pluralvote.com/article/model-methodology.php) which has a step by step breakdown of the model.
            
            Plural Vote's polling model averages polls through a LOESS moving regression. The Electoral College vote and probability for each candidate to win the majority of electors are estimated using 20,000 Monte Carlo simulations.
            
            For more information on Plural Vote's Model and to see more graphics on Plural Vote's model go to [http://www.pluralvote.com/article/2020-forecast/](http://www.pluralvote.com/article/2020-forecast/)
            ''')]),
    
    html.Br(),
    html.Center(children=[
            dcc.Markdown(''' Click the link below to access Sean Le Van's Github Page. Chase The White House is not responsible for any of the code or resources on any Github pages other than our own.
            ''')]),
    html.Center(children=[
        html.Div(children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'25%', 'width':'25%','marginRight':10,'marginBottom':0})],href='https://github.com/seanelevan/Plural-Vote'),
           
    ])]),

           
    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    
    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopta, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Science. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])]),

twitter_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
   html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),
    
    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Back to our Main Page', href='/',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About US', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),
    
    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),

    html.Center(children=[html.H1('Twitter Model')]),
    
    html.Div(id='Twitter Model'),
    html.Center(children=[html.H2('Map on 10/16')]),
    html.Center(children=[dcc.Graph(figure=tm_map_adj)]),
    html.Br(),
    html.Center(children=[html.H3('Methodology')]),
    html.Center(children=[
            dcc.Markdown(''' Our twitter model is based on tweet sentiment and 538's polling average. The tweets were scrapped through two packages looking for tweets 
            containing the phrases "Biden", "Trump", and "Election 2020". In total we've gathered over 2,000,000 tweets since August containing these phrases. 
            From there, we clean the data and use TextBlob to perform Sentiment Analysis. Each tweet is given a polarity and then determined to be positive, negative or neutral.
            We found that the scrapping packages we used included advertisement texts, so we querry the tweets for only tweets containing Trump or Biden and have either a positive or negative
            sentiment. We also screen the tweets are only from one Username and it removes any tweet that mentions both President Trump and Former Vice President Joe Biden. 
            Since we cannot determine who the tweet is about without manually checking each tweet, this is the easiest way of dealing with these tweets. Previous Twitter models will use the 
            count of tweets and overall sentiment ratio to determine the winner, but our dataset had President Trump having more tweets about him and Former Vice President Joe Biden having a 
            higher overall sentiment. In comparisson, 2016 models showed President Trump with more tweets with positive sentiment than Hillary Clinton.'''),
            
            dcc.Markdown('''To deal with this, we developed our own method by using a ratio of positive tweets divided by the sum of positive and negative tweets towards a candidate. 
            With these ratios, we calculate the estimated vote share of the incumbent party by finding the percent of the sum of the positive ratios caused by the incumbent party nominee and subtracting the independent vote.
            For 2020, President Donald Trump is predicted to receive 45.8% of the National Vote. In comparrison, our Twitter Model predicted Hillary Clinton would have a National Vote of 48.3%.
            In 2016, Hillary Clinton had 48.2% of the national vote. It is important to note our 2016 Model only uses 80,000 for our sample size. They were gather from Novemeber 3rd to Novemeber 7th.
            Our State Polling section is the same used as with our other models that predict the National Vote total of incumbents. We use [538's Polling Averages](https://projects.fivethirtyeight.com/polls/president-general/national/)
            as our base polls for the state. 538 calculates each state's current polling by averaging polls available based on grades assigned by 538 for the pollster. This data is made publically 
            available by 538. We calculate the difference between 538's polling average incumbent vote and our predicted vote and apply this difference to all the states. As an example,
            if a candidate has 40% of the vote nationally, but our model predicts that they will receive 50% of the vote, we will add 10% to 538's polling average for each state.
            The challenging party's nominee's vote total is calculated by subtracting the average national independent vote share over the previous 5 Presidential elections. For 2020, this number is 2.7%.
            This is our estimate for how much of the 2020 Presidential vote will go to 3rd parties. The challenger's national vote is equal to 100 - incumbent predicted - independent vote share avg. 
            This gives Former Vice President a predicted National Vote Share of 51.5% with rounding.'''),
            
            dcc.Markdown('''We use our 538 polling average method for this model because most tweets do not have a location tagged with the tweet. We also do not use an bot filtering or accounts connected to different organization.
            While we believe that only allowing one tweet per user in our sample solves this problem, it is important to recognize this. 
            ''')]),
    html.Br(),
    html.Center(children=[
            dcc.Markdown(''' Click the link below to access the Chase the White House Github Page.
            ''')]),
    html.Center(children=[
        html.Div(children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'25%', 'width':'25%','marginRight':10,'marginBottom':0})],href='https://github.com/bgrogers/ChaseTheWhiteHouse/'),])]),
    html.Br(),
    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopta, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Science. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])
        
jhk_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
   html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),


    html.Br(),

    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('Back to our Main Page', href='/', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About Us', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),
    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),
    html.Br(),
    html.Center(children=[html.H1('JHK Forecasts')]),
    
    html.Div(id='JHK Forecasts'),
    html.Center(children=[dcc.Link('Click here to go to JHK Forecast\'s Website', href='https://projects.jhkforecasts.com/presidential-forecast/')]),
    html.Br(),
    html.Center(children=[html.H2('Map on 10/26')]),
    html.Center(children=[dcc.Graph(figure=jhk_map)]),
    html.Center(children=[dcc.Link('Click here to go to JHK Forecast\'s Website', href='https://projects.jhkforecasts.com/presidential-forecast/')]),
    html.Br(),
    html.Center(children=[
            dcc.Markdown(''' 
            JHK Forecasts is a project created by Jack Kersting. His Twitter account is @jhkersting and his website is https://projects.jhkforecasts.com/
            JHK's model is based on four parts: polls, fundamentals, Expert Ratings, and state similarity ratings. For an example of an Expert Rating, please check out Sabato's Crystal Ball
            as he is one of the experts used by JHK. 
            
            One of the fundamentals used is Partisan Lean of a state based on it's previous election history. The other fundamental is an economic indicator calculated by Jack.
            The indicator is created by standardizing different indexes with Jobs, Stock Market, Income, Industrial Production, Personal Expenditures, Inflation, GDP, Dollar Index, Yield Curve,
            and consumer sentiment. Overall the fundamental section of this model has currently effectively 0 effect on the output as the model shifts more towards polling as the election gets closer
            as many other models do.
            
            Jack calculates his polling averages using [538's Pollster Ratings.](https://projects.fivethirtyeight.com/pollster-ratings/)
            He weights the rating of a poll based on the pollster rating and the recency of the poll. 
            
            The 5 expert ratings in the Model are [Sabato's Crystall Ball](http://centerforpolitics.org/crystalball/2020-president/),
            [Cook Political Report](https://cookpolitical.com/), [Inside Elections](https://insideelections.com/ratings/president), 
            [Bitecofer's Model](https://cnu.edu/wasoncenter/2019/07/01-2020-election-forecast/), and [Politico](https://www.politico.com/2020-election/race-forecasts-and-predictions/president/).
            
            The state similarity is found by comparing states demographics, location, and partisan lean.
            
            The output is calculated using 20,000 monte carlo simulations to calulate the win percentage of each state for each candidate. More information on this model can be found at [JHK Forecast's Website](https://projects.jhkforecasts.com/presidential-forecast/forecast_methodology).
            
            ''')]),
    html.Br(),
    html.Center(children=[
            dcc.Markdown(''' Click the link below to access Jack Kersting's Github Page. Chase The White House is not responsible for any of the code or resources on any Github pages other than our own.
            ''')]),

    html.Center(children=[
        html.Div(children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'25%', 'width':'25%','marginRight':10,'marginBottom':0})],href='https://github.com/jhkersting/jhkforecasts'),
           
    ])]),
    html.Br(),       
    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopta, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Sciene. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])
    
about_layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['background'],'border-style': 'double'},children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CapstoneHeaderLogo.jpg',
                    style={'height':'95%', 'width':'100%','marginRight':10,'marginBottom':0})],href='https://datascience.virginia.edu/'),
           
    ])]),
    
    html.Br(),
    
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'}, children = [
            html.Div( children = [
            dcc.Link('Economist Model', href='/Economist', style={'marginRight': 30}),
            dcc.Link('Princeton Election Consortium', href='/PEC', style={'marginRight': 30}),
            dcc.Link('Plural Vote', href='/Plural_Vote', style={'marginRight': 30}),
            dcc.Link('JHK Forecasts', href='/JHK_Forecasts', style={'marginRight': 30}),
            dcc.Link('Fair Vote Equation Model', href='/Fair_Vote_Equation',)],
                style={ 'display': 'inline-block'}),
        html.Br(),
        html.Div( children = [
            dcc.Link('Sabato Crystal Ball', href='/Sabato_Crystal_Ball', style={'marginRight': 30}),
            dcc.Link('Time For Change Model', href='/Time_For_Change',style={'marginRight': 30}),
            dcc.Link('Twitter Model', href='/Twitter_Model',style={'marginRight': 30}),
            dcc.Link('Bayesian Model', href='/Bayesian_Model',style={'marginRight': 30}),
            dcc.Link('About Us', href='/About_Us',)],
                style={ 'display': 'inline-block'})])]),

    html.Br(),
    html.Center(children=[
        html.Div([
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/CTWH3.png',
                    style={ 'height': '5%', 'width': '20%' }) ], style={'marginLeftt': 20},href='/About_Us')])]),
    
    

    html.Center(children=[html.H1('Who We Are')]),
    html.Center(children = [
        dcc.Markdown('''Chase the White House is a project created by University of Virginia School of Data Science Graduate Students Ben Rogers,
                Chad Sopta, Matt Thomas, and Spencer Marusco. Our goal is to study different models used to predict the 2020 Presidential Election
                with the final goal of creating our own model. These models range from fundamental linear regression models to more complicated
                Machine Learning Models. All models replicated have all the credit going to the orinigal creators of those models. All Model pages
                will include links to the creator's website and other ways to connect to the model creator. Those links are also available below.
                Thank you to each of these model creators for sharing how their code was created as this fosters a community of learning how to improve
                our knowledge of predicting Presidential Elections. All of the code is either available on our Github page linked in the top right or
                available on the models website. We consider it fundamental to any study of Election Forecasting to share code to fully understand the methods
                used. While every individual has their own intrinsic biases, we commit that all of our effort is to make an unbiaed prediction of the
                2020 U.S. Presidential Election. Special thanks to Professor Jonathan Kropko to all his help in creating this project.''')]),
    
    html.Br(),
    html.Center(children=[
            dcc.Markdown(''' Click the link below to access the Chase the White House Github Page.
            ''')]),
    html.Br(),
    html.Center(children=[
        html.Div(children= [         
            html.A([
                html.Img(
                    src='https://raw.githubusercontent.com/bgrogers/ChaseTheWhiteHouse/master/images/GitHub_Logo.png',
                    style={'height':'25%', 'width':'25%','marginRight':10,'marginBottom':0})],href='https://github.com/bgrogers/ChaseTheWhiteHouse/'),])]),
    
    html.Br(),
    html.Center(children=[dcc.Link('Go back to home', href='/')]),
    html.Br(),
    html.Center(children=[
        html.Div(style={'backgroundColor': colors['header'],'border-style': 'double'},children= [
            dcc.Markdown(''' This project is the creation of Ben Rogers, Chad Sopata, Matt Thomas, and Spencer Marusco for the University of Virginia School of Data Sciene. 
            All models are the product of their creators and all credit goes to them. Chase the White House does not endorse and candidate and is not tied to an organization not listed.
            Remember to vote!''')])])])



@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Economist':
        return Economist_layout
    elif pathname == '/Time_For_Change':
        return tfc_layout
    elif pathname == '/Fair_Vote_Equation':
        return fve_layout
    elif pathname == "/Sabato_Crystal_Ball":
        return sabato_layout
    elif pathname == '/Bayesian_Model':
        return bayesian_layout
    elif pathname == '/Twitter_Model':
        return twitter_layout
    elif pathname =='/Plural_Vote':
        return pv_layout
    elif pathname =='/PEC':
        return pec_layout
    elif pathname == '/JHK_Forecasts':
        return jhk_layout
    elif pathname == '/About_Us':
        return about_layout
    else:
        return index_page

#PORT = os.environ.get('PORT')
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
#if __name__ == '__main__':
#    app.run_server(debug=True, port=PORT)


# In[ ]:




