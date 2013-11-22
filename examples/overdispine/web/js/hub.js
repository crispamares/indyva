define(['WsRpc'],
function() {
    var WsRpc = require('WsRpc');

    var Hub = function(server, path, port){
	var self = this;

	path = path || 'ws';
	port = port || 8081;
	server = server || 'localhost:'+String(port);

	this._subscriptions = {};
	this._rpc = WsRpc.instance();
	this._rpc.call('HubSrv.new_gateway',['gtws','ws', port]).then( 
	    function () {
		self.ws = new WebSocket('ws://' + server + '/' + path);	
	    	self.ws.onmessage = function(event) { self._onmessage(event); };
	    });

	//this.ws.onopen = function(event) { self._onopen(); };
	//this.ws.onclose = function(event) { self._onclose(); };
    };

    /// Holding the WebSocket on default getsocket.
    Hub.prototype.ws = null;
    /// Object topic: callback
    Hub.prototype._subscriptions = {};
    /// The installed instance
    Hub.prototype._instance = null;

    Hub.instance = function() {
	if (Hub.prototype._instance == null) Hub.prototype._instance = new Hub();
	return Hub.prototype._instance;
    };
    Hub.prototype.install = function() {
	if (Hub.prototype._instance) throw new Error("Hub already installed");
	Hub.prototype._instance = this;
    };
    
    Hub.prototype.publish = function(topic, msg) {
	return this._rpc.call('HubSrv.publish',[topic, msg]);
    };

    Hub.prototype._subscribe = function(topic, callback, only_once, context) {
	context = context || null;
	var new_topic = ! Boolean(this._subscriptions[topic]);
	this._subscriptions[topic] = this._subscriptions[topic] || [];
	this._subscriptions[topic].push({only_once: only_once || false, 
					 callback: callback,
					 context: context});
	if (new_topic) {
	    if (only_once)
		return this._rpc.call('HubSrv.subscribe_once',['gtws', topic]);	    
	    else
		return this._rpc.call('HubSrv.subscribe',['gtws', topic]);	    
	}

	return true;
    };

    Hub.prototype.subscribe = function(topic, callback, context) {
	return this._subscribe(topic, callback, false, context);
    };

    Hub.prototype.subscribe_once = function(topic, callback, context) {
	return this._subscribe(topic, callback, true, context);
    };

    Hub.prototype.unsubscribe = function(topic, callback, context) {
	context = context || null;
	var subscriptions = this._subscriptions[topic] || [];
	var i=0, length= subscriptions.length, subs = null;
	for (;i < length;i++) {
	    if (subscriptions[i].callback === callback &&
	       !context || subscriptions[i].context === context) {
		subscriptions.splice(i, 1);
		
		// Adjust counter and length for removed item
                i--;
                length--;
	    }
	}
	if (!callback || subscriptions.length == 0)
	    delete this._subscriptions[topic];
	    return this._rpc.call('HubSrv.unsubscribe',['gwts', topic]);
	return true;
    };

    Hub.prototype.internal_publish = function(topic, msg) {
	var subscriptions = this._subscriptions[topic] || [];
	var i=0, length = subscriptions.length, subs = null;
	for (;i < length; i++) {
	    subs = subscriptions[i];
	    subs.callback.apply(subs.context, [topic, msg]);
	    if (subs.only_once)
		this.unsubscribe(topic, subs.callback, subs.context);
	}
    };

    Hub.prototype._onmessage = function(event) {
	var data = JSON.parse(event.data);

	this.internal_publish(data.topic, data.msg);
    };
    return Hub;
});
