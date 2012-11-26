var session = null;
function _session() {
    return session;
}
scinfo._session = _session;

// The map of objects that provide rpc calls
var rpcObjects = [];


function connectServer(conf) {

    conf = conf || {};
    var wsuri = conf.wsuri || "ws://" + window.location.hostname + ":9000";	

    var deferred = when.defer();
    var resolver = deferred.resolver;

    // connect to WAMP server
    ab.connect(wsuri, 
	       // WAMP session was established
	       function (s) {
		   session = s;

		   // establish a prefix, so we can abbreviate procedure URIs ..
		   _.map(rpcObjects, function(o) {
			     session.prefix(o.name, "http://scinfo.io/" + o.name +"#");
			 });

		   console.log("Connected to " + wsuri);
		   resolver.resolve(session);
	       },

	       // WAMP session is gone
	       function (code, reason) {
		   session = null;
		   if (code == ab.CONNECTION_UNSUPPORTED) {
		       window.location = "http://autobahn.ws/unsupportedbrowser";
		   } else {
		       alert(reason);
		       resolver.reject(code, reason);
		   }
	       }
	      );
    return deferred.promise;
}
scinfo.connectServer = connectServer;

