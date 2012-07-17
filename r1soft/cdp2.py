import xmlrpclib
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.propagate = False

class SimpleClient(xmlrpclib.ServerProxy): pass

def format_xmlrpc_url(hostname, auth_token, use_ssl=True, port=None):
    """Make a proper XML-RPC URL from the given information
    """
    if use_ssl:
        proto = 'https'
    else:
        proto = 'http'
    if port is None:
        if use_ssl:
            port = 8085
        else:
            port = 8084

    url = '{proto}://{username}:{password}@{hostname}:{port:d}/xmlrpc'.format(
        proto='https' if use_ssl else 'http',
        port=port,
        hostname=hostname,
        username=auth_token[0],
        password=auth_token[1])
    logging.debug('Created XML-RPC URL: %s' % url)
    return url
