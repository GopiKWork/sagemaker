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

REGIONS = ["us-east-1", "us-east-2", "us-west-1","us-west-2"]

def get_user_profle_detail(region,domainId,user_profile_name):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    response = sm_client.describe_user_profile(DomainId=domainId,UserProfileName=user_profile_name)
    return response

def get_user_profiles(region,domainId):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    user_profiles = []
    
    #List all user profiles of the domain
    response = sm_client.list_user_profiles(DomainIdEquals=domainId,MaxResults=100)
    user_profiles = response["UserProfiles"]
    while "NextToken" in response:
        response = sm_client.list_user_profiles(NextToken=response["NextToken"],DomainIdEquals=domainId,MaxResults=100)
        user_profiles.extend(response["UserProfiles"])
    
    for up in user_profiles:
        up_detail = get_user_profle_detail(region,domainId,up['UserProfileName'])
        up['UserProfileArn'] = up_detail['UserProfileArn']
        up['Status'] = up_detail['Status']
        if 'SecurityGroups' in up_detail['UserSettings']:
            up['InVPC'] = 'Yes'
        else:
            up['InVPC'] = 'No'
        
        if 'SingleSignOnUserIdentifier' in up_detail:
            up['SSO-ID'] = up_detail['SingleSignOnUserIdentifier']
        else:
            up['SSO-ID'] = ''
        up['ExecutionRole'] = up_detail['UserSettings']['ExecutionRole']
        up['Region'] = region
        
    
    return user_profiles

@st.cache_data(persist="disk")   
def get_user_profiles_multi(items):
    user_profiles = []
    for p in items:
        region = p['Region']
        domainId = p['DomainId']
        user_profiles.extend(get_user_profiles(region,domainId))
    return user_profiles
      
def get_domains(region):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    studio_domains = sm_client.list_domains()['Domains']
    for d in studio_domains:
        d['Region'] = region
    return studio_domains

@st.cache_data(persist="disk")     
def get_domains_multi(regions):
    domains = []
    for region in regions:
        sm_client = boto3.Session().client('sagemaker',region_name=region)
        sd = sm_client.list_domains()['Domains']
        for d in sd:
            d['Region'] = region
        domains.extend(sd)
    return domains


def to_domains_df(domains):
    cols = ['Region',
            'DomainId',
            'DomainName',
            'Status',
            'CreationTime',
            'LastModifiedTime',
            'DomainArn',
            'Url'
           ]
    df = pd.json_normalize(domains)
    return df[cols]

def aggrid_interactive_table(df,selection_mode="multiple",key="grid"):
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()
    options.configure_selection(selection_mode="multiple",use_checkbox=True,rowMultiSelectWithClick=False,pre_selected_rows=0)
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        reload_data=False,
        #key=key
    )
    return selection

def aggrid_interactive_table_single(df,key):
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()
    options.configure_selection(selection_mode="single",use_checkbox=True,rowMultiSelectWithClick=False)
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        reload_data=False,
        key=key
    )
    return selection

def aggrid_table(df,key):
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()
    options.configure_selection(selection_mode="single",use_checkbox=False,rowMultiSelectWithClick=False,pre_selected_rows=0)
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        reload_data=True,
        key=key
    )
    return selection


def get_space_detail(region,domainId,space_name):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    response = sm_client.describe_space(DomainId=domainId,SpaceName=space_name)
    return response

def get_spaces(region,domainId):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    spaces = []
    
    #List all spaces of the domain
    response = sm_client.list_spaces(DomainIdEquals=domainId,MaxResults=100)
    spaces = response["Spaces"]
    while "NextToken" in response:
        response = sm_client.list_user_profiles(NextToken=response["NextToken"],DomainIdEquals=domainId,MaxResults=100)
        spaces.extend(response["Spaces"])
    
    for sp in spaces:
        sp_detail = get_space_detail(region,domainId,sp['SpaceName'])
        sp['SpaceArn'] = sp_detail['SpaceArn']
        sp['Status'] = sp_detail['Status']
        sp['Region'] = region
        
    
    return spaces

@st.cache_data(persist="disk")  
def get_spaces_multi(items):
    spaces = []
    for p in items:
        region = p['Region']
        domainId = p['DomainId']
        spaces.extend(get_spaces(region,domainId))
    return spaces


def get_space_app_details(region,domainId,space_name,app_name,app_type):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    return sm_client.describe_app(DomainId=domainId,SpaceName=space_name,AppType=app_type,AppName=app_name)

def get_user_app_details(region,domainId,user_profile_name,app_name,app_type):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    return sm_client.describe_app(DomainId=domainId,UserProfileName=user_profile_name,AppType=app_type,AppName=app_name)


@st.cache_data(persist="disk")   
def get_apps(region,include_default_apps):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    apps = []
    #List all user /shared space apps
    paginator = sm_client.get_paginator('list_apps')
    iterator = paginator.paginate(PaginationConfig={'PageSize': 100})
    for app_page in iterator:
        for ua in app_page['Apps']:
            domainId = ua['DomainId']
            if 'UserProfileName' in ua:
                ua['OwnerType'] = 'User'
                user_profile_name = ua['UserProfileName']
                ua['Owner'] = ua['UserProfileName']
                del ua['UserProfileName']
                upd = get_user_app_details(region,domainId,user_profile_name,ua['AppName'],ua['AppType'])
                if 'FailureReason' in upd:
                    ua['FailureReason'] = upd['FailureReason']

                ua['LastUserActivityTimestamp'] = upd['LastUserActivityTimestamp']
                ua['InstanceType'] = upd['ResourceSpec']['InstanceType']

                if 'LifecycleConfigArn' in upd['ResourceSpec']:
                    ua['LifecycleConfigArn'] = upd['ResourceSpec']['LifecycleConfigArn']
                ua['SageMakerImageArn'] = upd['ResourceSpec']['SageMakerImageArn']
            elif 'SpaceName' in ua:
                ua['OwnerType'] = 'Shared Spaces'
                space_name = ua['SpaceName']
                ua['Owner'] = ua['SpaceName']
                del ua['SpaceName']
                spd = get_space_app_details(region,domainId,space_name,ua['AppName'],ua['AppType'])
                if 'FailureReason' in spd:
                    ua['FailureReason'] = spd['FailureReason']

                ua['LastUserActivityTimestamp'] = spd['LastUserActivityTimestamp']
                ua['InstanceType'] = spd['ResourceSpec']['InstanceType']

                if 'LifecycleConfigArn' in spd['ResourceSpec']:
                    ua['LifecycleConfigArn'] = spd['ResourceSpec']['LifecycleConfigArn']
                ua['SageMakerImageArn'] = spd['ResourceSpec']['SageMakerImageArn']              
        apps.extend(app_page['Apps'])
    
    if not include_default_apps:
        apps = [a for a in apps if a['AppName'] != 'default']
    return apps

def delete_user_app(region,domainId,user_profile_name,app_name,app_type):
    st.write(f'Deleting User app Region: {region}; Domain: {domainId}; User Profile: {user_profile_name}; AppType: {app_type}; AppName: {app_name}')        
    sm_client = boto3.Session().client('sagemaker',region_name=region)    
    sm_client.delete_app(DomainId=domainId,UserProfileName=user_profile_name,AppType=app_type,AppName=app_name)

def delete_spaces_app(region,domainId,space_name,app_name,app_type):
    st.write(f'Deleting spaces app Region: {region}; Domain: {domainId}; Spaces: {space_name}; AppType: {app_type}; AppName: {app_name}')    
    sm_client = boto3.Session().client('sagemaker',region_name=region)    
    sm_client.delete_app(DomainId=domainId,SpaceName=space_name,AppType=app_type,AppName=app_name)

def to_apps_df(apps):
    cols = ['DomainId',
        'OwnerType',
        'Owner',
        'AppType',
        'AppName',
        'Status',
        'LastUserActivityTimestamp',
        'InstanceType',
        'SageMakerImageArn'
       ]
    df = pd.json_normalize(apps)
    if not df.empty:
        if 'LifecycleConfigArn' in df.columns:
            cols.append('LifecycleConfigArn')
        if 'FailureReason' in df.columns:
            cols.append('FailureReason')
        return df[cols]
    else:
        return df

def get_instances_by_user(apps):
    response = {}
    instances = list(set([a['InstanceType'] for a in apps]))
    for i in instances:
        response[i] = list(set([a['Owner'] for a in apps if a['InstanceType'] == i]))
    return response

def get_app_metrics(apps):
    app_count = len(apps)
    domain_count = len(set([a['DomainId'] for a in apps]))
    user_app_count = len([a['AppName'] for a in apps if a['OwnerType'] == 'User' ])
    shared_space_app_count = len([a['AppName'] for a in apps if a['OwnerType']!= 'User'])
    return domain_count,app_count,user_app_count,shared_space_app_count,get_instances_by_user(apps)



def _get_sessions(sagemaker_login_url):
    session = requests.Session()
    login_resp = session.get(sagemaker_login_url)
    base_url = sagemaker_login_url.partition("?")[0].rpartition("/")[0]
    api_base_url = base_url + "/jupyter/default"
    
    # Wait until ready
    if "_xsrf" not in session.cookies:
        app_status = "Unknown"
        while app_status not in {"InService", "Terminated"}:
            time.sleep(2)
            app_status = session.get(
                f"{base_url}/app?appType=JupyterServer&appName=default"
            ).text
        ready_resp = session.get(api_base_url)

    terminal_sessions = sessions = session.get(f"{api_base_url}/api/terminals").json()
    sessions = session.get(f"{api_base_url}/api/sessions").json()
    sessions_by_instances = {}
    for s in sessions:
        session_id = s['id']
        instance_type = s['kernel']['instance_type']
        resource_name = s['name']
        resource_path = s['path']
        resource_type = s['type']
        execution_status = s['kernel']['execution_state']
        last_activity = s['kernel']['last_activity']
        app_name = s['kernel']['app_name']
        if not instance_type in sessions_by_instances:
            sessions_by_instances[instance_type] = {}
        
        if not app_name in sessions_by_instances[instance_type]:
            sessions_by_instances[instance_type][app_name] = []
        
        sessions_by_instances[instance_type][app_name].append({
            'id': session_id,
            'resource_name' : resource_name,
            'resource_type': resource_type,
            'execution_status' : execution_status,
            'last_activity': last_activity,
            'resource_path':resource_path
        })
    return sessions_by_instances, terminal_sessions

def get_user_sessions(region,domain_id,user_profile_name):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    sagemaker_login_url = sm_client.create_presigned_domain_url(DomainId=domain_id,UserProfileName=user_profile_name)["AuthorizedUrl"]
    return _get_sessions(sagemaker_login_url)


def get_spaces_sessions(region,domain_id,space_name,user_profile_name):
    sm_client = boto3.Session().client('sagemaker',region_name=region)
    sagemaker_login_url = sm_client.create_presigned_domain_url(DomainId=domain_id,SpaceName=space_name,UserProfileName=user_profile_name)["AuthorizedUrl"]
    return _get_sessions(sagemaker_login_url)

def get_kernel_metrics(sessions_by_instances):
    instances = len(sessions_by_instances.keys())
    app_count = 0
    notebooks = 0
    others = 0
    for apps in sessions_by_instances.values():
        for an,s in apps.items():
            app_count += 1
            notebooks += len([n for n in s if n['resource_type']=='notebook'])
            others += len([n for n in s if n['resource_type'] !='notebook'])
    return instances,app_count,notebooks,others
    