#!/usr/bin/env python

import sys
from apicem_service import ApicemService

class RbacService(ApicemService):
    """ The RbacService class handels the role based access controll functionality provided by the APIC-EM API
    """

    def __init__(self, session, apic):
        super(RbacService, self).__init__(session, apic)

    def authenticate(self):
        """ uses the rbac api to create an x-auth-token which will be used 
            to authenticate the session for all subsequent api calls.
        """
        auth_url = self.create_url('ticket')
        body = {
            'username': self.apic['user'],
            'password': self.apic['password']
        }
        headers={'Content-Type' : 'application/json'}
        self.session.headers.update(headers)
        try:
            result = self.session.post(url=auth_url, json=body, headers=headers, verify=False)
            result.raise_for_status()
        except result.exception.RequestException as e:
            print(e)
            sys.exit(1)
        print(result.text)
        token = result.json()['response']['serviceTicket']
        self.session.headers.update({'x-auth-token': token})