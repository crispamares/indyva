#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Nov 7, 2013

@author: crispamares
'''

import vtk
import sys, os
import zmq

from indyva.external.tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from indyva.external.tinyrpc.transports.zmq import ZmqClientTransport
from indyva.external.tinyrpc import RPCClient
import json
import random

class SpineView(object):
    def __init__(self, ren, rw, actor_list):
        self.ren = ren
        self.rw = rw
        self.actor_list = actor_list

    def show_actor(self, i):
        self.ren.RemoveAllViewProps()
        actor = self.actor_list[i % len(self.actor_list)]
        self.ren.AddActor(actor)
        self.ren.ResetCamera()
        self.rw.Render()

def read_vrml(rw, input_filename):    
    importer = vtk.vtkVRMLImporter()
    importer.SetFileName(input_filename)
    importer.Read()
    importer.SetRenderWindow(rw)
    importer.Update()

    rw.Render()
    
    ren = importer.GetRenderer()
    actors = ren.GetActors()
    actors.InitTraversal()
    actors_list = [actors.GetNextActor() 
        for _x in range(ren.GetNumberOfPropsRendered())]
    return actors_list, ren
    
        
class zmqPoller(object):
    def __init__(self, socket):
        self.socket = socket
        self.callbacks = {}
        
    def run(self,obj,event):
        if self.socket.poll(0):
            topic, json_msg = self.socket.recv_multipart()
            msg = json.loads(json_msg)
            print topic, msg
            if topic in self.callbacks:
                self.callbacks[topic](topic, msg)
            iren = obj
            iren.GetRenderWindow().Render()
        
    
         
    
def main():
    input_filename = sys.argv[1]
    
    rw = vtk.vtkRenderWindow()
    rwi = vtk.vtkRenderWindowInteractor()           
    rwi.SetRenderWindow(rw)    
    rwi.Initialize()                                                   
    
    actors_list, ren = read_vrml(rw, input_filename)
    #===========================================================================
    #  Prepare Lights
    #     Necessary because the scene can have a static light
    #===========================================================================
    ren.RemoveAllLights()
    ren.CreateLight() 
    
    view = SpineView(ren, rw, actors_list)
    view.show_actor(1)
    
    ctx = zmq.Context()
    transport = ZmqClientTransport.create(ctx, 'tcp://127.0.0.1:8090')
    rpc_client = RPCClient(JSONRPCProtocol(), transport)
    hub = rpc_client.get_proxy(prefix='HubSrv.')
    
    gw = hub.new_gateway('gwzmq', 'zmq', 8091)
    print 'created', gw
    
    hub.subscribe('gwzmq', 'spine_selected')
    socket = ctx.socket(zmq.SUB)
    socket.connect('tcp://127.0.0.1:8091')
    socket.setsockopt(zmq.SUBSCRIBE,'')
    
    poller = zmqPoller(socket)
    poller.callbacks['spine_selected'] = lambda t,m : view.show_actor(random.randint(0,1000))

    rwi.AddObserver('TimerEvent', poller.run)
    _timerId = rwi.CreateRepeatingTimer(100);
    
    
    rwi.Start()
    print 'yeah'
    

    

if __name__ == '__main__':
    print "running"
    main()