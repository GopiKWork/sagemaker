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
    
Links to SageMaker Studio architecture deep dive and terminate idle applications to manage costs.
    
    ''')
    
    st.title('SageMaker Studio- Additional Resources') 
    st.write('### _Studio architecture_')
    st.image("pages/images/SM-Studio-architecture.jpg",width=650)
    st.markdown('''
    * A Studio domain is a logical aggregation of an Amazon Elastic File System (Amazon EFS) volume, a list of users authorized to access the domain, and configurations related to security, application, networking, and more. A domain promotes collaboration between users where they can share notebooks and other artifacts with other users in the same domain.

* Each user added to the Studio domain is represented by a user profile. This profile contains unique information about the user with in the domain, like the execution role for the user, the Posix user ID of the user’s profile in the Amazon EFS volume, and more.

* An app is an application running for a user in the domain, implemented as a Docker container.

[Reference](https://aws.amazon.com/blogs/machine-learning/dive-deep-into-amazon-sagemaker-studio-notebook-architecture/)

    ''')
    st.write('')
    st.markdown('''    
    ### _Shutdown of studio applications_
    * [Auto-shutdown Studio Notebooks](https://github.com/aws-samples/sagemaker-studio-auto-shutdown-extension/blob/main/README.md)
    * [Shutting Down Amazon SageMaker Studio Apps on a Scheduled Basis](https://medium.com/swlh/shutting-down-amazon-sagemaker-studio-kernelgateways-automatically-with-aws-lambda-41e93afef06b)
    * [Customizing SageMaker Studio](https://towardsdatascience.com/run-setup-scripts-automatically-on-sagemaker-studio-15222b9d2f8c)
    ''')
    st.write('')
    st.markdown('''
### _Cost tracking with tags_

* SageMaker Studio automatically tags resources such as training jobs, processing jobs, experiments, pipelines, and model registry entries with their respective sagemaker:domain-arn. 
* SageMaker also tags the resource with the sagemaker:user-profile-arn or sagemaker:space-arn to designate the resource creation at an even more granular level.
* Similar to other AWS resources, you can use automated tagging to monitor costs by using tools such as AWS Budgets and AWS Cost Explorer. 

More info in below blogs: 
* [Optimizing Cost with SageMaker](https://aws.amazon.com/blogs/machine-learning/optimizing-costs-for-machine-learning-with-amazon-sagemaker/)
* [Ensure efficient Compute Resources](https://aws.amazon.com/blogs/machine-learning/ensure-efficient-compute-resources-on-amazon-sagemaker/)
* [Resource tagging with SageMaker](https://aws.amazon.com/blogs/machine-learning/set-up-enterprise-level-cost-allocation-for-ml-environments-and-workloads-using-resource-tagging-in-amazon-sagemaker/)
* [SageMaker Domain management](https://aws.amazon.com/blogs/machine-learning/separate-lines-of-business-or-teams-with-multiple-amazon-sagemaker-domains/)   
    
    ''')
    st.write('')

# Run main method
if __name__ == '__main__':
    main()