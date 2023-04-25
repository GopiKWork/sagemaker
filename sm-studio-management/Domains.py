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


Domain: An Amazon SageMaker Domain consists of an associated Amazon Elastic File System (Amazon EFS) volume; a list of authorized users; and a variety of security, application, policy, and Amazon Virtual Private Cloud (Amazon VPC) configurations. Users within a Domain can share notebook files and other artifacts with each other. An account can have multiple Domains. 

UserProfile: A user profile represents a single user within a Domain. It is the main way to reference a user for the purposes of sharing, reporting, and other user-oriented features. This entity is created when a user onboards to the Amazon SageMaker Domain. 

Shared space: A shared space consists of a shared JupyterServer application and shared directory. All users within the Domain have access to the shared space. All user profiles in a Domain have access to all shared spaces in the Domain. 

    ''')
    
    #st.title('User Profiles & Shared Spaces')
    #region = st.selectbox("###### Select a region",REGIONS)
    #sm_domains_json = get_domains(region)
    st.title('SageMaker Studio-Domains')    
    sm_domains_json = get_domains_multi(REGIONS)
    
    region_count = len(set([d['Region'] for d in sm_domains_json]))
    domains_count = len(sm_domains_json)    
    
    items = []
    for i in sm_domains_json:
        items.append({'Region':i['Region'],'DomainId':i['DomainId'], 'DomainName':i['DomainName']})
    
    sm_user_profiles = get_user_profiles_multi(items)
    sm_spaces =  get_spaces_multi(items)
    
    region_count = len(set([d['Region'] for d in sm_domains_json]))
    domains_count = len(sm_domains_json)
    user_profiles_count = len(sm_user_profiles)
    shared_spaces_count = len(sm_spaces)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Regions", region_count )
    with col2:
        st.metric("Domains", domains_count )
    with col3:
        st.metric("User Profiles", user_profiles_count)
    with col4:
        st.metric("Shared Spaces", shared_spaces_count)
    
    
    st.write('##### Domains')
    #domain_selection= aggrid_interactive_table(pd.json_normalize(items))
    domain_selection= aggrid_interactive_table(to_domains_df(sm_domains_json),"Domains")
    
    if domain_selection and len(domain_selection['selected_rows']) > 0:
       
        items = [i['DomainId'] for i in domain_selection['selected_rows']]
        
        st.write('##### User Profiles')
        df = pd.json_normalize([up for up in sm_user_profiles if up['DomainId'] in items])
        #aggrid_table(df,"UserProfilesGrid")
        st.dataframe(df.style.hide(axis="index"),use_container_width=True)
        st.write('')
        
        st.write('##### Shared Spaces')
        df = pd.json_normalize([sp for sp in sm_spaces if sp['DomainId'] in items])
        #aggrid_table(df,"SpacesGrid")
        st.dataframe(df.style.hide(axis="index"),use_container_width=True)
        st.write('')
    else:
        if st.button('Clear Cache',key='CacheClear'):
            get_domains_multi.clear()
            get_user_profiles_multi.clear()
            get_spaces_multi.clear()


# Run main method
if __name__ == '__main__':
    main()