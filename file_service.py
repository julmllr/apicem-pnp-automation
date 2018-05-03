#!/usr/bin/env python

import sys
import os
import requests
from apicem_service import ApicemService

class FileService(ApicemService):
    """ The FileService class handels all the functionality regarding file manipulation 
        that is availiable through the APIC-EM API"""

    def __init__(self, session, apic):
        super(FileService, self).__init__(session, apic)

    def upload_file(self, namespace, filepath):
        url = self.create_url(path='file/%s' % namespace)
        print('POST %s' % url)
        with open(filepath , 'r') as f:
            name = os.path.basename(filepath)
            files = {'fileUpload': (name, f)}
            try:
                headers={ 'x-auth-token': self.session.headers['x-auth-token']}
                result = requests.post(url, files=files, headers=headers, verify=False)
                print(result.text)
            except requests.exceptions.RequestException  as cerror:
                print('Error processing request', cerror)
                sys.exit(1)
        return result.json()

    def list_files(self, namespace):
        files = []
        url = self.create_url(path='file/namespace/%s' % namespace)
        print('Getting %s' % url)
        try:
            result = self.session.get(url, verify=False)
        except requests.exceptions.RequestException  as cerror:
            print('Error processing request', cerror)
            sys.exit(1)
        for file in result.json()['response']:
            files.append({'name': file['name'], 'id': file['id']})
        return files

    def delete_file(self, fileid):
        url = self.create_url(path='file/%s' % fileid)
        print('Delete %s' % url)
        try:
            result = self.session.delete(url, verify=False)
        except requests.exceptions.RequestException  as cerror:
            print('Error processing request', cerror)
            sys.exit(1)
        return result.json()

    def delete_files(self, namespaces):
        for item in namespaces:
            files = self.list_files(namespace=item)
            for file in files:
                self.delete_file(file['id'])

    def list_namespaces(self):
        url = self.create_url(path='file/namespace')
        print('Delete %s' % url)
        try:
            result = self.session.get(url, verify=False)
        except requests.exceptions.RequestException  as cerror:
            print('Error processing request', cerror)
            sys.exit(1)
        return result.json()['response']