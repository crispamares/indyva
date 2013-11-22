
define(["when"],
function() {
    var when = require('when');

    var WsRpc = function(server, path, port){
	var self = this;

	path = path || 'ws';
	port = port || 8080;
	server = server || 'localhost:'+String(port);

	this._out_queue = [];
	this._futures = {};
	this.ws = new WebSocket('ws://' + server + '/' + path);
	this.ws.onmessage = function(event) { self._onmessage(event); };
	this.ws.onopen = function(event) { self._flush(); };
    };

    /// Holding the WebSocket on default getsocket.
    WsRpc.prototype.ws = null;
    /// Object <id>: when.deferred
    WsRpc.prototype._futures = {};
    /// The next JSON-WsRpc request id.
    WsRpc.prototype._current_id = 1;
    /// The not ready queue
    WsRpc.prototype._out_queue = [];
    /// The installed instance
    WsRpc.prototype._instance = null;

    // Class method
    WsRpc.instance = function() {
	if (WsRpc.prototype._instance == null) WsRpc.prototype._instance = new WsRpc();
	return WsRpc.prototype._instance;
    };
    WsRpc.prototype.install = function() {
	if (WsRpc.prototype._instance) throw new Error("WsRpc already installed");
	WsRpc.prototype._instance = this;
    };

    /**
     * @fn call
     * @memberof WsRpc
     *
     * @param method     The method to run on JSON-RPC server.
     * @param params     The params; an array or object.
     * @return		 A when.promise 
     */
    WsRpc.prototype.call = function call(method, params) {
	// Construct the JSON-RPC 2.0 request.
	var request = {
	    jsonrpc : '2.0',
	    method  : method,
	    params  : params,
	    id      : this._current_id++  // Increase the id counter to match request/response
	};

	var deferred = when.defer();
	this._futures[request.id] = deferred;

	var request_json = JSON.stringify(request);
	this._send(request_json);

	return deferred.promise;
    };   

    /**
     * Internal method that sends a message through the Web Socket
     * only if the connection is ready, otherwise the message is
     * queued until the _flush method is called.
     * 
     * @fn _send
     * @memberof WsRpc
     *
     * @param request_json     The JSON-RPC request.
     */
    WsRpc.prototype._send = function(request_json) {
	if (this.ws.readyState == 1) {
	    this.ws.send(request_json);
	}
	else {
	    this._out_queue.push(request_json);
	}
    };

    WsRpc.prototype._flush = function (){
	var self = this;
	this._out_queue.forEach(
	    function(request_json) {
		self.ws.send(request_json);
	    });
	this._out_queue = [];
    };

    /**
     * Internal handler for the websocket messages.  It determines if
     * the message is a JSON-RPC response, and if so, tries to couple
     * it with a given deferred. Otherwise, it falls back to given
     * external onerror-handler, if any.
     *
     * @param event The websocket onmessage-event.
     */
    WsRpc.prototype._onmessage = function(event) {
	// Check if this could be a JSON RPC message.
	try {
	    var response = JSON.parse(event.data);

	    if (typeof response === 'object'
		&& 'jsonrpc' in response
		&& response.jsonrpc === '2.0') {

		/// This is a bad response. Failure in the protocol
		if ('error' in response && response.id === null) {
		    if (typeof this.onerror === 'function') {
			this.onerror(event);
		    }
		}
		else if (this._futures[response.id]) {
		    // Get the deferred.
		    var deferred = this._futures[response.id];		
		    // Delete the deferred from the storage.
		    delete this._futures[response.id];

		    if ('result' in response) {
			// Resolve with result as parameter.
			deferred.resolve(response.result);
		    }
		    else if ('error' in response){
			// Reject with the error object as parameter.
			deferred.reject(response.error);		    
		    }
		}

		return;
	    }
	}
	catch (err) {
	    // Probably an error while parsing a non json-string as json.  
	    // All real JSON-RPC cases are
	    // handled above, and the fallback method is called below.
	    console.log('*** Error no handled', err, this);
	}
	// This is not a JSON-RPC response. 
	new Error('This is not a JSON-RPC response' + String(response));
    };
    return WsRpc;
}


);

