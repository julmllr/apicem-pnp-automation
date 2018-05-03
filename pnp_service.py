#!/usr/bin/env python

import sys
import requests
from apicem_service import ApicemService

class PnpService(ApicemService):
    """ The PnpService class handels all the functionality regarding the Plug&Play module 
        of the APIC-EM controller that is availiable through the api"""

    def __init__(self, session, apic):
        super(PnpService, self).__init__(session, apic)

    def create_project(self, project_name):
        url = self.create_url(path='pnp-project')
        body = [{'siteName': project_name}]
        print ('POST URL %s' % url)
        print ('Creating project %s' % project_name)
        try:
            result = self.session.post(url, json=body, verify=False)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        print(result.text)
        task_id = result.json()['response']['taskId']
        task = self.service_task(task_id)
        return task

    def project_name_to_id(self, project_name):
        url = self.create_url(path='pnp-project')
        search_url = url + '?siteName=%s&offset=1&limit=10' %project_name
        print('GET: %s'  % search_url)
        try:
            result = self.session.get(search_url, verify=False)
            result.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        print(result.text)
        response = result.json()['response']
        project_id = 0
        if len(response) == 1:
            project_id = response[0]['id']
        elif len(response) > 1:
            print('multiple project_ids with same project name: %s', project_name)
            project_id = response[0]['id']
        else:
            print('project not found %s', project_name)
            sys.exit(1)
        return project_id

    def add_project_device(self, project_name, serial, platform, host, config_id=None, template_config_id=None):  
        project_id = self.project_name_to_id(project_name)
        url = self.create_url(path=('pnp-project/%s/device' % project_id))
        print('url%s' % url)
        data = {
            'serialNumber': serial,
            'platformId': platform,
            'hostName': host,
            'pkiEnabled': True
        }
        if template_config_id is not None:
            data['templateConfigId'] = template_config_id
        if config_id is not None:
            data['configId'] = config_id
        try:
            result = self.session.post(url, json=[data,], verify=False)
            result.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        task_id = result.json()['response']['taskId']
        task = self.service_task(task_id)
        return task

    def list_projects(self):
        url = self.create_url(path='pnp-project')
        print('Getting %s' % url)
        try:
            result = self.session.get(url, verify=False)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        return result.json()

    def delete_project(self, project_id):
        url = self.create_url(path=('pnp-project/%s?deleteRule=1&deleteDevice=1' % project_id))
        print('delete %s : ' % url)
        try:
            result = self.session.delete(url, verify=False)
            result.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        task_id = result.json()['response']['taskId']
        task = self.service_task(task_id)
        return task

    def delete_projects(self):
        projects = self.list_projects()
        for project in projects['response']:
            self.delete_project(project['id'])

    def find_template_file_id(self, template_name):
        url = self.create_url(path='pnp-file/template')
        try:
            result = self.session.get(url, verify=False)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        response = result.json()['response']
        configfile_id = 0
        for item in response:
            if item['name'] == (template_name):
                configfile_id = item['id']
                print('Template: ' + template_name + ' matches Template-ID: ' + configfile_id)
        return configfile_id

    def find_template(self, template_id):
        url = self.create_url(path='template')
        data = [{'templateId': template_id}]
        return_id = 0
        try:
            result = self.session.get(url, json=data, verify=False)
        except requests.exceptions.RequestException  as e:
            print(e)
            sys.exit(1)
        response = result.json()['response']
        if response['errorCode']:
            print('Error finding template ' + response['errorCode'])
        else:
            return_id = response['id']
        return return_id

    def find_template_by_file_id(self, file_id):
        template_id = 0
        template_list = self.list_templates()
        for values in template_list:
            if values['fileId'] == file_id:
                template_id = values['id']
        return template_id

    def add_template(self, file_id):
        template_id = self.find_template_by_file_id(file_id)
        if template_id == 0:
            url = self.create_url(path='template')
            body = [{'fileId':file_id}]
            try:
                result = self.session.post(url, json=body, verify=False)
            except requests.exceptions.RequestException  as e:
                print(e)
                sys.exit(1)
            task_id = result.json()['response']['taskId']
            task = self.service_task(task_id)
            if task['isError'] is not True:
                task_progress = task['progress'].split(',')
                template_id = 0
                for item in task_progress:
                    if 'id' in item:
                        template_id = item.split(':')[-1]
                        template_id = template_id.replace('"', '')
                        template_id = template_id.replace('}', '')
            else:
                print('Failed to create a new template from File')
        else:
            print('Template already exists')
        return template_id

    def delete_template(self, template_id):
        url = self.create_url(path=('template/%s' % template_id))
        try:
            result = self.session.delete(url, verify=False)
        except requests.exceptions.RequestException  as e:
            print(e)
            sys.exit(1)
        task_id = result.json()['response']['taskId']
        task = self.service_task(task_id)
        return task

    def list_templates(self):
        url = self.create_url(path='template')
        try:
            result = self.session.get(url, verify=False)
            print(result.text)
        except requests.exceptions.RequestException  as e:
            print(e)
            sys.exit(1)
        response = result.json()['response']
        id_list = []
        for item in response:
            id_list.append({'id': item['id'], 'fileId': item['fileId']})
        return id_list

    def delete_template_config(self, template_config_id):
        url = self.create_url(path=('template-config/%s' % template_config_id))
        try:
            result = self.session.delete(url, verify=False)
        except requests.exceptions.RequestException  as e:
            print(e)
            sys.exit(1)
        task_id = result.json()['response']['taskId']
        task = self.service_task(task_id)
        return task

    def list_template_configs(self):
        url = self.create_url(path='template-config')
        try:
            result = self.session.get(url, verify=False)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        response = result.json()['response']
        id_list = []
        for item in response:
            id_list.append(item['id'])
        return id_list

    def delete_all_template_configs(self):
        template_config_list = self.list_template_configs()
        for template_config in template_config_list:
            self.delete_template_config(template_config)

    def delete_all_templates(self):
        template_list = self.list_templates()
        for values in template_list:
            self.delete_template(values['id'])

    def create_config_from_template(self, template_id, variables=None):
        config_property = {}
        url = self.create_url(path='template-config')
        if variables is None:
            config_property = {'hostname': 'Default'}
        else:
            config_property = variables
        body = [{'templateId': template_id, 'configProperty': config_property, 'name' : template_id}]
        try:
            result = self.session.post(url, json=body, verify=False)
        except requests.exceptions.RequestException  as e:
            print(e)
            sys.exit(1)
        task_id = result.json()['response']['taskId']
        task = self.service_task(task_id)
        if task['isError'] is not True:
            task_progress = task['progress'].split(',')
            gen_config_id = 0
            for item in task_progress:
                if 'id' in item:
                    gen_config_id = item.split(':')[-1]
                    gen_config_id = gen_config_id.replace('"', '')
                    gen_config_id = gen_config_id.replace('}', '')
        return gen_config_id

    def extract_variables(self, device):
        variables = {}
        for (k, v) in device.items():
            if 'Var:' in k:
                k = k.split(':')[-1]
                variables[k] = v
        return variables

    def create_template_config(self, device):
        """ get id of the template file associated to the device in the project
        """
        template_file_id = self.find_template_file_id(device['Template'])
        template_id = self.add_template(template_file_id)
        generated_config_id = self.create_config_from_template(template_id, self.extract_variables(device))
        return {'templateConfigId': template_id, 'configId' : generated_config_id}