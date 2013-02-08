#!/usr/bin/env python

import suds.client
import logging

logger = logging.getLogger('cdp-add-agent')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
logger.propagate = False

class MetaClient(object):
    def __init__(self, url_base, **kwargs):
        self.__url_base = url_base
        self.__init_args = kwargs
        self.__clients = dict()

    def __getattr__(self, name):
        c = self.__clients.get(name, None)
        logger.debug('Accessing SOAP client: %s' % name)
        if c is None:
            logger.debug('Client doesn\'t exist, creating: %s' % name)
            c = suds.client.Client(self.__url_base % name, **self.__init_args)
            self.__clients[name] = c
        return c

def get_wsdl_url(hostname, namespace, use_ssl=True, port_override=None):
    if use_ssl:
        proto = 'https'
    else:
        proto = 'http'
    if port_override is None:
        if use_ssl:
            port = 9443
        else:
            port = 9080
    else:
        port = port_override
    url = '%s://%s:%d/%s?wsdl' % (proto, hostname, port, namespace)
    logging.debug('Creating WSDL URL: %s' % url)
    return url

if __name__ == '__main__':
    import sys
    import re

    try:
        cdphost = sys.argv[1]
        cdpuser, cdppass = sys.argv[2].split(':')
    except IndexError:
        logger.error('Usage: %s <r1soft host> <CDP user>:<CDP pass>') 
        sys.exit(1)

    logger.info('Using CDP host: %s', cdphost)
    logger.info('Using CDP credentials: %s / %s', cdpuser, cdppass)

    client = MetaClient(get_wsdl_url(cdphost, '%s'),
        username=cdpuser, password=cdppass)

    #agents = client.Agent.service.getAgents()
    policies = client.Policy2.service.getPolicies()

    for policy in policies:
      if policy['state'] in ('UNKNOWN', 'ERROR') and policy['enabled'] == True:
        print policy['name']

