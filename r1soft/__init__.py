import optparse

def create_basic_option_parser():
    """Create an OptionParser with the standard options needed to create a
    MetaClient
    """
    parser = optparse.OptionParser()
    parser.add_option('-r', '--r1soft-host', dest='hostname',
        help='R1Soft server to add host to')
    parser.add_option('-u', '--username', dest='username',
        default=os.environ.get('CDP_USER', 'admin'),
        help='R1Soft server API username')
    parser.add_option('-p', '--password', dest='password',
        default=os.environ.get('CDP_PASS', ''),
        help='R1Soft server API password')
    parser.add_option('-P', '--port', dest='port',
        type=int, default=9443,
        help='R1Soft server API port')
    parser.add_option('--no-ssl', dest='use_ssl',
        type=bool, default=True, action='store_false',
        help='Use HTTP instead of HTTPS for API access')
    return parser
