import argparse
import ConfigParser
import socket
import random

from indyva.external.lru_cache import lru_cache


default_options = [
    ("zmq_server", dict(default=False, action='store_true', help="Run the ZMQ Server")),
    ("zmq_port", dict(type=int, default=18000, help="The port number of the ZMQ server")),
    ("ws_server", dict(default=False, action='store_true', help="Run the WebSocket Server")),
    ("ws_port", dict(type=int, default=18081, help="The port number of the WebSocket server")),
    ("web_dir", dict(default='web', help="The directory where the index.html is placed")),
#    ("web_server", dict(default=False, action='store_true', help="Run the Web Server")),
#    ("web_port", dict(type=int, default=18080, help="The port number of the Web server")),
    ("use_random_port", dict(default=False, action='store_true', help="Let the system find free ports inside the port range")),
    ("port_max_tries", dict(type=int, default=100, help="Maximum number of port finding attempts to make")),
    ("min_port", dict(type=int, default=10000, help="The lower port of the range")),
    ("max_port", dict(type=int, default=20000, help="The upper port of the range"))
]


def parse_args_and_config(options=None, description=None):
    '''
    This function reads the configuration from three sources. If the
    user specify a ``config_file`` the config file is read. Then the
    rest of argv is parsed overwriting the previous
    configuration.

    The configuration options accepted by this function are described
    in :data:`default_options`. You can change these options by
    providing an options argument.

    :param options: List of options like arguments are specified in argparse
    :param str description: A description of what the program does, printed in the help prompt

    :returns: The parsed arguments as an object (Namespace)
    '''
    if options is None:
        options = default_options

    # Turn off help, so we print all options in response to -h
    config_parser = argparse.ArgumentParser(add_help=False)
    config_parser.add_argument("-c", "--config_file",
                               help="Specify configuration file", metavar="FILE")
    args, remaining_argv = config_parser.parse_known_args()

    defaults = { k:v['default'] for k, v in options }

    if args.config_file:
        config = ConfigParser.SafeConfigParser()
        config.read([args.config_file])
        config_defaults = dict(config.items("Core"))

        defaults.update(config_defaults)

    # Don't surpress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        description=description,
        # Inherit options from config_parser
        parents=[config_parser],
        # Print default values in the help message
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('--version', action='version', version='PROGRAM VERSION')
    for option in options:
        parser.add_argument("--" + option[0], **option[1])

    parser.set_defaults(**defaults)

    args = parser.parse_args(remaining_argv)

    return args



def get_random_port(port_range=None, max_tries=None):
    '''
    Return a free port in a range

    :param port_range: (int,int) The min and max port numbers
    :param max_tries: The maximum number of bind attempts to make
    :return port: int, the port ready to use
    '''
    if port_range is None or max_tries is None:
        config = parse_args_and_config()

    port_range = (config.min_port, config.max_port) if port_range is None else port_range
    max_tries = config.port_max_tries if max_tries is None else max_tries

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(max_tries):
        try:
            port = random.randrange(port_range[0], port_range[1])
            s.bind(('127.0.0.1',port))
        except socket.error as e:
            if not e.errno == socket.errno.EADDRINUSE:
                raise
        else:
            s.close()
            return port
    raise Exception("Could not find a free random port.")
