#!/usr/bin/env python

import requests
from pnp_service import PnpService 
from file_service import FileService
from rbac_service import RbacService

class ApicemApi:
    """ APIC-EM API class. Provides easy to use interface which handles the interaction
        with the APIC-EM Controler HTTP API.
    """

    def __init__(self, ip, user, password, api_version='v1'):
        """ setting up parameteres for using the APIC-EM API:
            ip, user, password, api_version
            if no values for the API Version is given, a default value will be assigned.
        """
        self.apic = {
            'ip' : ip,
            'user': user,
            'password' : password,
            'api_version' : api_version
        }
        self.session = requests.Session()
        self.rbac = RbacService(self.session, self.apic)
        self.pnp = PnpService(self.session, self.apic)
        self.file = FileService(self.session, self.apic)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
        print('close')

    def edit_session(self,session, headers):
        """ Edits a persistant Session to interact with the APIC-EM API.
        """
        session.header.update(headers)