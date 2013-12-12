# -*- coding: utf-8 -*-
'''
Created on 18/07/2013

@author: jmorales
'''

import zmq
import json
import time
import datetime

service_name = 'DateSrv'
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
    print 'srv_description'
    return {'now': [],
            'tomorrow': [('days','int, optional=1, The number of days after after today')]}

#------------------------------------------------------------------------------

def main():
    print 'running'
    
    msg_id = 1 # id of jsonrpc requests 
    ctx = zmq.Context()
    
    req_socket = ctx.socket(zmq.REQ)
    req_socket.connect('tcp://127.0.0.1:8090')
    
    rep_socket = ctx.socket(zmq.REP)
    rep_socket.bind(service_endpoint)
    
    public_methods = {'now': now,
                      "tomorrow": tomorrow,
                      "srv_description": srv_description}
    
    #===========================================================================
    #        Expose the new service with the exposed methods
    #===========================================================================
    msg = pack_msg('FrontSrv.expose',
                   [service_name, service_endpoint, srv_description()],
                    msg_id)
    
    req_socket.send(msg)
    response = json.loads(req_socket.recv())
    print 'expose: ', response
    if response.get('error'):
        raise Exception('Error trying to expose {0} at {1}: {2}'
                        .format(service_name, service_endpoint, response['error']))
    

    #===========================================================================
    #        Expose public methods
    #===========================================================================
    #
    #  The methods has to be exposed explicitly in the expose method. 
    #
    #  But, in order to support reconnection (planned for the future) the remote
    #    service has to support a srv_description call at any point, 
    #    so the easiest way is implementing this method as a regular public method.     
    #
    #  The srv_description is mandatory, and usually will be called on reconnection.
    #
    
    #===========================================================================
    #        Serve forever
    #===========================================================================
    while True:
        req_msg = rep_socket.recv()
        print 'recv', req_msg
        try:
            req = json.loads(req_msg)
            # Invoke the requested method
            method =  public_methods[req['method']]
            if 'params' in req:
                result = method(req['params'])
            else:
                result = method()
                
            print 'Called: {0}   ->  {1}'.format(req, result)
            response = {"jsonrpc": "2.0", 
                        "result": result, 
                        "id": req['id']}
            rep_socket.send(json.dumps(response))
        except Exception, e:
            # This error handle SHOULD be comprehensive
            # see the specification: http://www.jsonrpc.org/specification
            error = {"jsonrpc": "2.0", 
                     "error": {"code": -32000, "message": str(e)}, 
                     "id": None}
            rep_socket.send(json.dumps(error))
    
if __name__ == '__main__':
    main()
    