# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''

import zmq
import json
import time
import datetime

service_name = 'DateService'
service_endpoint = 'tcp://127.0.0.1:8095'

def pack_msg(method, params, id=1):
    ''' This is the call that other languages has to implement '''
           
    msg = {'jsonrpc': '2.0',
           'id': id, 
           'method': method,
           'params':params
       }
    json_msg = json.dumps(msg)
    return json_msg 

#===============================================================================
#   Public Methods
#===============================================================================

def now():
    return time.time()

def tomorrow(days=1):
    tomorrow = datetime.date.today() + datetime.timedelta(days)
    return str(tomorrow)

def srv_description():
    return {'now': [],
            'tomorrow': [('days','int, optional=1, The number of days after after today')]}

#------------------------------------------------------------------------------

def main():
    print 'running'
    
    msg_id = 1 # id of jsonrpc requests 
    ctx = zmq.Context()
    
    req_socket = ctx.socket(zmq.REQ)
    req_socket.connect('tcp://127.0.0.1:8090')
    
    res_socket = ctx.socket(zmq.REP)
    res_socket.bind(service_endpoint)
    
    public_methods = {'now': now,
                      "tomorrow": tomorrow,
                      "srv_description": srv_description}
    
    #===========================================================================
    #        Expose the new service
    #===========================================================================
    msg = pack_msg('FrontSrv.expose', [service_name, service_endpoint], msg_id)
    req_socket.send(msg)
    response = json.loads(req_socket.recv())
    if response.get('error'):
        raise Exception('Error trying to expose {0} at {1}: {2}'
                        .format(service_name, service_endpoint, response['error']))
    
    
    #===========================================================================
    #        (no) Expose public methods
    #===========================================================================
    #
    #  The methods could be exposed explicitly but will turn the implementation
    # of external services into more verbose protocol. 
    #
    #  If no good reason is fount, the srv_description will be optional as well 
    #
    
    #===========================================================================
    #        Serve forever
    #===========================================================================
    while True:
        req_msg = res_socket.recv()
        try:
            req = json.loads(req_msg)
            # Invoke the requested method
            result = public_methods[req['method']](req['params'])
            response = {"jsonrpc": "2.0", 
                        "result": result, 
                        "id": req['id']}
            req_msg.send(json.dumps(response))
        except Exception, e:
            # This error handle SHOULD be comprehensive
            # see the specification: http://www.jsonrpc.org/specification
            error = {"jsonrpc": "2.0", 
                     "error": {"code": -32000, "message": str(e)}, 
                     "id": None}
            res_socket.send(json.dumps(error))
    
if __name__ == '__main__':
    main()