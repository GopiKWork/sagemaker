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
    
    st.sidebar.image('pages/images/SageMakerIcon.png')
    st.sidebar.markdown('''
    
SageMaker Studio's KernelGateway architecture allows the notebook server to communicate with kernels running on remote hosts. KernelGateway and Jupyter kernels run on different hosts. 

Kernel apps run on remote instances and users can spawn multiple notebooks and terminals using each kernel app.

You can view utilization by selecting a user profile or a Shared Space and terminate a kernel application. 
    
    ''')
    st.title('SageMaker Studio-Utilization')     
    
    region = st.selectbox("###### Region",REGIONS)
    sm_domains_json = get_domains(region)
    items = []
    sm_user_profiles = []
    sm_shared_spaces = []
    df_users = pd.DataFrame(columns=['Region','DomainId'])
    df_spaces = pd.DataFrame(columns=['Region','DomainId'])
    for i in sm_domains_json:
        items.append({'Region':i['Region'],'DomainId':i['DomainId'], 'DomainName':i['DomainName']})
    
    if len(items) > 0:
        sm_user_profiles = get_user_profiles_multi(items)
        for u in sm_user_profiles:
            u['Owner'] = u['UserProfileName']
        df_users = pd.json_normalize(sm_user_profiles)
        
        if len(sm_user_profiles) > 0:
            cols = ['Region',
                    'DomainId',
                    'Owner'
                   ]
            df_users = df_users[cols]
            df_users['OwnerType'] = 'User'
            
        sm_shared_spaces = get_spaces_multi(items)
        for s in sm_shared_spaces:
            s['Owner'] = s['SpaceName']
        df_spaces = pd.json_normalize(sm_shared_spaces)
        if len(sm_shared_spaces) > 0:
            cols = ['Region',
                    'DomainId',
                    'Owner'
                   ]
            df_spaces = df_spaces[cols]
            df_spaces['OwnerType'] = 'SharedSpace'
        
    df = pd.concat([df_users,df_spaces])
    st.write('')

    col1, col2= st.columns(2)
    with col1:
        st.write("###### User Profiles & Shared Spaces")
        selection = aggrid_interactive_table_single(df,"UP-SS-Grid" + region)  
    
    if selection and len(selection['selected_rows']) > 0:
        r = selection['selected_rows'][0]
        domain_id = r['DomainId']
        owner = r['Owner']
        region = r['Region']
        owner_type = r['OwnerType']

        st.write(f'Resources launched by {owner_type}: :green[{owner}] in Domain :green[{domain_id}]')
        
        if owner_type == 'User':
            sessions_by_instances,terminal_sessions = get_user_sessions(region,domain_id,owner)
            instances,apps,notebooks,others = get_kernel_metrics(sessions_by_instances)
        else: #Shared Spaces
            default_user = [u for u in sm_user_profiles if (u['DomainId'] == domain_id) and (u['Region'] == region)][0]['Owner']
            sessions_by_instances,terminal_sessions = get_spaces_sessions(region,domain_id,owner,default_user)
            instances,apps,notebooks,others = get_kernel_metrics(sessions_by_instances)
            
        with col2:
            col11,col12,col13 = st.columns(3)
            st.write(' ')
            with col12:
                st.metric('Instances',instances)
                st.metric('Applications',apps)
                st.metric('Terminals',len(terminal_sessions))
            with col13:
                st.metric('Notebooks',notebooks)
                st.metric('Other resources',others)
        for instance_type,apps in sessions_by_instances.items():
            with st.expander(f'## Instance: :green[{instance_type}]',expanded=True):
                for app_name,sessions in apps.items():
                    app_type = 'KernelGateway' 
                    st.write(f' Application: :blue[{app_name}]')
                    if st.button(label='Terminate',key=app_name):
                        txt = 'Domain: ' + domain_id + ' Owner: ' + owner + ' OwnerType: ' +  owner_type + ' AppType: ' + app_type  + ' AppName: ' + app_name
                        if owner_type == 'User':
                            delete_user_app(region,domain_id,owner,app_name,app_type)
                        else:
                            delete_spaces_app(region,domain_id,owner,app_name,app_type)
                            
                    st.dataframe(sessions)

    else:
        if st.button('Clear Cache',key='CacheClear'):
            get_user_profiles_multi.clear()
            get_spaces_multi.clear()
            
    
# Run main method
if __name__ == '__main__':
    main()