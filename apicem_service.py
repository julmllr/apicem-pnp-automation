#!/usr/bin/env python

import sys
import json
import requests
from task import Task

class ApicemService(object):
    """ parent class for all APIC-EM api services. 
        provides functionality commonly used by all services like waiting on completion of a task.
    """

    def __init__(self, session, apic):
        self.apic = apic
        self.session = session

    def create_url(self, path):
        """ helper function to create the http api urls
        """
        url = 'https://%s/api/%s/%s' % (self.apic['ip'], self.apic['api_version'], path)
        return url

    def service_task(self, task_id):
        url = self.create_url('task/%s' % task_id)
        task = Task()
        while True:
            try:
                result = self.session.get(url=url, verify=False)
                result.raise_for_status()
            except requests.exceptions.RequestException  as e:
                print(e)
                sys.exit(1)
            response = result.json()['response']
            if 'endTime' in response:
                return response
            else:
                task.wait(task_id)
            if response['isError'] == True:
                raise task.TaskError('Task %s had error %s' % (task_id, response['progress']))
        return response
