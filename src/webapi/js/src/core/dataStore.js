
var dataStore = {
    name: 'data_store',
    loadData: function (analysisName) {
	console.log('rpc');
	session.call("data_store:load_data", analysisName).then(function (d) {
		console.log("ok, data loaded");
		console.log(d);
		});
    }

};
rpcObjects.push(dataStore);
scinfo.dataStore = dataStore;