#!/usr/bin/env python
''' This script is automating the onboarding process of new network devices using the Cisco APIC-EM server.
    New devices can be added through batch processing using a .CSV list input file containing all the required data.
    There is also the option to automatically generate device configuration files based on templates. 
    This script was developed for demonstration purposes in a lab and ignores certificate issues. 
'''

import csv
import os
import argparse
import requests
from apicem_api import ApicemApi

def path(relative_path):
    """ helper function to get the file path
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

def read_device_data(device_file):
    """ helper function to read the required dataset from a predefined csv file
    """
    devices=[]
    with open(device_file, 'rt') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            devices.append(row)
    return devices
    
def sites_in_data(device_data):
    """ helper function to list all projects in the dataset
    """
    sites = []
    for device in device_data:
        if device['Site'] not in sites:
            sites.append(device['Site'])
    return sites

def templates_in_data(device_data):
    """ helper function to list all template files in the dataset
    """
    templates = []
    for device in device_data:
        if device['Template'] not in templates:
            templates.append(device['Template'])
    return templates

def delete_all(apic_api):
    """ helper function to clean all prior projects and templates 
    """
    apicem_api.file.delete_files(namespaces=['config','template'])
    apicem_api.pnp.delete_projects()
    apicem_api.pnp.delete_all_template_configs()
    apicem_api.pnp.delete_all_templates()

if __name__ == "__main__":
    """ initiating the apic-em pnp project automation. Uses the following arguments
        'server_ip' 'username' 'password' 'data.csv'
    """
    requests.packages.urllib3.disable_warnings() 
    parser = argparse.ArgumentParser(description='Script to automate the process of creating new APIC-EM PnP Projects based on a CSV input File') 
    parser.add_argument("ip", type=str, help="IP address of the APIC-EM server")
    parser.add_argument("user", type=str, help="Username required logging into the APIC-EM server")
    parser.add_argument("password", type=str, help="Password required logging into the APIC-EM server")
    parser.add_argument("file", type=str, help="File which holds the information required to create new projects and devices")
    parser.add_argument("-c", "--cleanup", action="store_true",help="delete all projects and files from APIC-EM")
    args = parser.parse_args()
    ip = args.ip
    user = args.user
    password = args.password
    file = args.file
    delete = args.cleanup
    device_data = read_device_data(path(file))
    sites = sites_in_data(device_data)
    templates = templates_in_data(device_data) 

    with ApicemApi(ip,user,password) as apicem_api:
        apicem_api.rbac.authenticate()
        if delete:
            for site in sites:
                project_id = apicem_api.pnp.project_name_to_id(site)
                apicem_api.pnp.delete_project(project_id)
            for template in templates:
                template_id = apicem_api.pnp.find_template_file_id(template)
                apicem_api.file.delete_file(template_id)
        else:
            for site in sites:
                apicem_api.pnp.create_project(site)
            for template in templates:
                apicem_api.file.upload_file('template',path(template))
            for device in device_data:
                indentifiers = apicem_api.pnp.create_template_config(device)
                response = apicem_api.pnp.add_project_device(project_name=device['Site'], 
                                            serial=device['SerialNumber'], platform=device['PlatformId'], 
                                            host=device['Name'], config_id=None, template_config_id=indentifiers['configId'])
                print(response['progress'])    
    print('closed')




