# import dependencies
import streamlit as st
import numpy as np
import pandas as pd
import requests
import random
import glob, os, sys
import json
import logging
import base64
import matplotlib.pyplot as plt
from pathlib import Path
import boto3
import time

from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

from pages.shared.utils import *




def main():
    st.set_page_config(page_title='SageMaker Studio Management', page_icon=None, layout='wide', initial_sidebar_state='auto')
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 2rem;
                    padding-right: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)
    st.sidebar.image('pages/images/SageMakerIcon.png')
    st.sidebar.markdown('''
   
SageMaker Studio application supports the reading and execution experience of the user’s notebooks, terminals, and consoles. The type of app can be JupyterServer, KernelGateway, RStudioServerPro, or RSession. A user may have multiple apps active simultaneously.

You can terminate applications in bulk in a region across all domains.

    ''')
    st.markdown("""
    <style>
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
       overflow-wrap: break-word;
       white-space: break-spaces;
       color: orange;
       font-size: 120%;
    }
    </style>
    """
    , unsafe_allow_html=True)

    st.title('SageMaker Studio- Bulk Manage Applications')
    col1,col2 = st.columns(2)
    with col1:
        region = st.selectbox("###### Select a region",REGIONS)
    with col2:
        include_default_apps = st.checkbox("Include Default Apps")


    with st.form(key="formDelete"):
        apps_json = get_apps(region,include_default_apps)
        apps = to_apps_df(apps_json)
        domain_count,app_count,user_app_count,shared_space_app_count,ins_metrics = get_app_metrics(apps_json)
        ins_count = {}
        for k,v in ins_metrics.items():
            ins_count[k] = len(v)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Domains", domain_count )
            st.metric("Apps", app_count)
            st.metric("Instances",sum(list(ins_count.values())))
        with col2:
            st.metric("User", user_app_count)
            st.metric("Shared Spaces", shared_space_app_count)
        with col3:
            df = pd.DataFrame({'Instance':list(ins_count.keys()),'Count':list(ins_count.values())})
            fig = plt.figure(figsize = (5, 2))
            plt.bar(df['Instance'], df['Count'], color='red')
            plt.xlabel('Instance')
            plt.ylabel('Count')
            st.pyplot(fig)

        if not apps.empty:
            app_selection = aggrid_interactive_table(apps)
        
        delete_button = st.form_submit_button(label="Delete Applications")
        if delete_button and not apps.empty:
            for i in app_selection['selected_rows']:
                if i['OwnerType'] == 'User':
                    delete_user_app(region,i['DomainId'],i['Owner'],i['AppName'],i['AppType'])
                else:
                    delete_spaces_app(region,i['DomainId'],i['Owner'],i['AppName'],i['AppType'])                    
    if st.button('Clear Cache'):
        get_apps.clear()

    # Run main method
if __name__ == '__main__':
    main()