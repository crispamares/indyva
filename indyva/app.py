#! /usr/bin/env python
'''This module can be use as an executable to configure and run an
Indyva Kernel. You can also inherit from :class:`App` to make your own
core application.

Provides a ``CLI`` interface for the configuration and also allows to
set the configuration with a configuration file (ini syntax).

For more details::
    $ ./app.py --help

'''
import sys
try:
    import indyva
    print "indyva is found in the PYTHONPATH. Running version:", indyva.__version__
except:
    sys.path.append('..')
from indyva.core.kernel import Kernel
from indyva.facade.server import WSServer, ZMQServer
from indyva.core.configuration import (get_random_port, parse_args_and_config, default_options)


class App(object):
    '''
    This class provide an easy way of configure and run a kernel.

    ::
        app = App()         # Default configuration
        app.run()           # This is blocking
    '''
    def __init__(self, argv_options=None, config=None):
        '''You can provide a configuration if you don't want to parse the
        invocation args or a config file.

        :config object config: Is an Namespace (object) with the
        kernel configuration
        '''
        self.kernel = Kernel()
        options = default_options
        if argv_options is not None:
            options += argv_options
        if config is None:
            config = parse_args_and_config(options)
        self.config_services(config)
        self.config = config


    def config_services(self, config):
        '''Usually you don't have to invoke this method, is invoked in the
        ``__init__`` method.

        This method creates and adds to the kernel que services
        indicated in the configuration.

        Also configures the ports that those servers are going to use.

        :param object config: Is an Namespace (object) with the kernel configuration

        '''
        if config.zmq_server:
            zmq_port = self._guess_port(config, config.zmq_port)
            zmq_server = ZMQServer(port=zmq_port)
            self.kernel.add_server(zmq_server)

            print "* ZMQ Server listening on port: {0}".format(zmq_port)

        if config.ws_server:
            ws_port = self._guess_port(config, config.ws_port)
            ws_server = WSServer(port=ws_port, web_dir=config.web_dir)
            self.kernel.add_server(ws_server)

            print "* WebSocket Server listening on port: {0}".format(ws_port)
            print "* Serving web from: {0}".format(config.web_dir)

    def _guess_port(self, config, default=None):
        if config.use_random_port:
            port_range = (config.min_port, config.max_port)
            max_tries = config.port_max_tries
            port = get_random_port(port_range=port_range, max_tries=max_tries)
        elif default is not None:
            port = default
        else:
            raise Exception("Is impossible to get a free port")

        return port

    def run(self):
        self.kernel.run_forever()


if __name__ == '__main__':
    app = App()
    app.run()
