#  MRR (Monthly Recurring Revenue)
# - ARR (Annual Run Rate)
# - TAS (Tasa de Adquisición de Suscriptores)
# - LTV (Life Time Value)
# - Churn rate
# - Estatus de suscripción
# - Más lo que decidas incluir
#%%
import streamlit as st
import numpy as np
import pandas as pd
# %%
df = pd.read_excel('payments.xlsx',sheet_name='Hoja 1 - payments (2)',index_col=0, header=1)
df = df.reset_index().set_index('id')

# %%
#Converting to Datetime
df[['paid_at','refund_failed_at','failed_at','created_at','updated_at','deleted_at','required_action_at','refunded_at','attended_at','refund_pending_at']] = df[['failed_at','created_at','updated_at','deleted_at','required_action_at','refunded_at','attended_at','refund_pending_at','refund_failed_at','paid_at']].apply(pd.to_datetime)
df.head()
# %%
