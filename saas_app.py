# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# - MRR (Monthly Recurring Revenue)
# - ARR (Annual Run Rate)
# - TAS (Tasa de Adquisición de Suscriptores)
# - LTV (Life Time Value)
# - Churn rate
# - Estatus de suscripción
# - Más lo que decidas incluir

# %%
#Libs for ETL
import numpy as np
import pandas as pd

# %%
#Reading Excel using Pandas.
df = pd.read_excel('payments.xlsx',sheet_name='Hoja 1 - payments (2)',index_col=0, header=1)
df = df.reset_index().set_index('id')


# %%
#Converting to Datetime
df['paid_at'] = pd.to_datetime(df['paid_at'],infer_datetime_format=True)
df['failed_at'] = pd.to_datetime(df['failed_at'],infer_datetime_format=True)
df['created_at'] = pd.to_datetime(df['created_at'],infer_datetime_format=True)
df['updated_at'] = pd.to_datetime(df['updated_at'],infer_datetime_format=True)
df['deleted_at'] = pd.to_datetime(df['deleted_at'],infer_datetime_format=True)
df['required_action_at'] = pd.to_datetime(df['required_action_at'],infer_datetime_format=True)
df['refunded_at'] = pd.to_datetime(df['refunded_at'],infer_datetime_format=True)
df['attended_at'] = pd.to_datetime(df['attended_at'],infer_datetime_format=True)
df['refund_pending_at'] = pd.to_datetime(df['refund_pending_at'],infer_datetime_format=True)


# %%
#Cheking datetime format.
df.head()


# %%
#Resamling DataSet to Monthly
subscribed=df.groupby(['company_id',pd.Grouper(key='paid_at',freq='MS')])['amount'].sum()
subscribed

# %%
#Monthly Recurrent Revenue

MRR = subscribed.groupby('paid_at').sum().reset_index().rename(columns={'amount':'MRR','paid_at':'Date'})
MRR


# %%
# Annual Run Rate
MRR['ARR'] = MRR['MRR']*12


# %%
# Average Revenue per User
ARPU = subscribed.groupby('paid_at').mean().reset_index().rename(columns={'amount':'ARPU','paid_at':'Date'})
ARPU['ARPU'] = ARPU['ARPU'].astype(int)


# %%
#Churn Rate
# Total # of Customers that Cancel / Total # of Customers (at given Month)


# %%
#Total # of Customers 
tot_custM =  df.groupby(['company_id','paid_at'])['status'].count().reset_index()
tot_custM = tot_custM.resample('MS',on='paid_at')['status'].count().reset_index().rename(columns={'status':'Total_users','paid_at':'Date'})
 


# %%
#Total Canceled per company (check if this can be done by payer_id)
fail_custM = df[df['status']== 'failed']
fail_custM =  fail_custM.groupby(['company_id','failed_at'])['status'].count().reset_index()
fail_custM = fail_custM.resample('MS',on='failed_at')['status'].count().reset_index().rename(columns={'status':'Canceled','failed_at':'Date'})
fail_custM['Canceled'] = np.floor(fail_custM['Canceled']/4)
# fail_custM = fail_custM[fail_custM['Canceled']>=1] # if i want to ignore months with no cancelations.
canceled = fail_custM
canceled['Canceled']= fail_custM['Canceled'].astype(int)


# %%
#Churn rate and months estimated.
churn = canceled.merge(tot_custM, how='inner', on='Date')
churn['Churn_rate'] = churn.Canceled/churn.Total_users
churn['Months'] = 1/churn.Churn_rate


# %%
#CLV Customer Life time Value
#ARPU*churn(months)
CLV = ARPU.merge(churn,how='inner',on='Date')
CLV['CLV'] = CLV['ARPU']*CLV['Months']
CLV['CLV'] = CLV['CLV'].astype(int,errors='ignore')

# %%
#Metrics consolidation.
SAAS = CLV
SAAS['MRR'] = MRR['MRR']
SAAS['ARR'] = MRR['ARR']

SAAS


# %%
# Dash Config.
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import plotly.express as px


# %%
#Theme and Colors
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "SaaS Analytics: Understand Your Startup!"


# %%
#Figure and subplots

fig1 = make_subplots(rows=2, cols=2, start_cell="top-left",subplot_titles=("Monthly Recurring Revenue", "Annual Run Rate", "Average Revenue per User / Life Time Value","ChurnRate / Customers"),specs=[[{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": True}, {"secondary_y": True}]])      
fig1.add_trace(
    go.Bar(x=SAAS["Date"], y=SAAS["MRR"],name="MRR"),
    row=1, col=1
    )
    
fig1.add_trace(
    go.Bar(x=SAAS["Date"], y=SAAS["ARR"],name="ARR"),
    row=1, col=2
    )
fig1.add_trace(
    go.Scatter(x=SAAS["Date"], y=SAAS["ARPU"],name="ARPU"),
    row=2, col=1
    )
fig1.add_trace(
    go.Scatter(x=SAAS["Date"], y=SAAS["CLV"],name="CLTV",line=dict(dash='dash')),
    row=2, col=1,secondary_y=True
    )
# Set y-axes titles
fig1.update_yaxes(row=2, col=1,
        title_text="ARPU", 
        secondary_y=False)
fig1.update_yaxes(row=2, col=1,
        title_text="CLTV", 
        secondary_y=True)

fig1.add_trace(
    go.Scatter(x=SAAS["Date"], y=SAAS["Churn_rate"],name="Churn_rate" ,line=dict(dash='dash')),
    row=2, col=2)
fig1.add_trace(
    go.Scatter(x=SAAS["Date"], y=SAAS["Total_users"],name="Users"),
    row=2, col=2,secondary_y=True)
fig1.update_yaxes(row=2, col=2,
        title_text="Churn_Rate", 
        secondary_y=False)
fig1.update_yaxes(row=2, col=2,
        title_text="Users", 
        secondary_y=True)
fig1.update_layout(yaxis5=dict(tickformat=",.0%"))

fig1.update_layout(height=900, width=1100, title_text="Metrics",showlegend=False)


# %%
#App Layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📈", className="header-emoji"),
                html.H1(
                    children="SaaS Analytics", className="header-title"
                ),
                html.P(
                    children="Understand your Startup",
                    className="header-description",
                ),
            ],
            className="header",
        ),
html.Div(
    children=[
        html.Div(
            children=dcc.Graph(
                id="chart",
                config={"displayModeBar": False},
                figure=fig1
            ),
            className="card",
        ),
    ],
    className="wrapper",
    ),
    ]
)


# %%
#Main
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
