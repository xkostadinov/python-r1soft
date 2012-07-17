import suds.client
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.propagate = False

class SimpleClient(suds.client.Client): pass

class MetaClient(object):
    """A proxy object for child SimpleClients. Makes it easier to access
    the different SOAP WSDL endpoints.
    """
    def __init__(self, url_base, **kwargs):
        """Instantiate MetaClient

        kwargs is passed to each SimpleClient created
        """
        self.__url_base = url_base
        self.__init_args = kwargs
        self.__clients = dict()

    def __getattr__(self, name):
        logger.debug('Retrieving SOAP client for namespace: %s' % name)
        client = self.__clients.get(name, None)
        if client is None:
            logger.debug('Client doesn\'t exist, creating...')
            client = SimpleClient(self.__url_base % name, **self.__init_args)
            self.__clients[name] = client
        return client

def format_wsdl_url(hostname, namespace, use_ssl=True, port=None):
    """Make a proper WSDL URL from the given information
    """
    if use_ssl:
        proto = 'https'
    else:
        proto = 'http'
    if port is None:
        if use_ssl:
            port = 9443
        else:
            port = 9080
    url = '%s://%s:%d/%s?wsdl' % (proto, hostname, port, namespace)
    logging.debug('Created WSDL URL: %s' % url)
    return url
