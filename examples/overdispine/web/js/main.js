require.config({
    baseUrl: 'js',
    paths: {
        jquery: 'vendor/jquery.min',
	bootstrap: 'vendor/bootstrap.min',
	when: 'vendor/when',
	d3: 'vendor/d3.v3.min',
	vega: 'vendor/vega'
    }
});


requirejs(['jquery', 
	   'when', 
	   'bootstrap', 
	   'WsRpc',
	   'd3',
	   'vega',
	   'treemap'], 

function($, when, bootstrap, WsRpc, d3, vega ) {
    console.log('running');

    rpc = new WsRpc('localhost:8080', 'ws');
    var treemap = require("treemap");
    var view = new treemap("#overview"); 


    when.map( groupBySpine(),
	    function(pipeline) {return rpc.call('TableSrv.aggregate', ["spines_table", pipeline]);})
	.then(
	    function(views) {
		return when.map(views, function(view) {return rpc.call('TableSrv.get_data', [view]);});
	    })
	.then(
	    function (sizes) {
		var data = {
		    name: "sizes",
		    children: [
			   {name: "apical", children: sizes[0] },
			   {name: "basal", children: sizes[1] }
			   ]};
		view.setData(data);
		view.update();
	    });

});


function groupByDendriteId() {

    var apical_pipeline = [{$match: {dendrite_type:"apical"}},
		    {$project: {dendrite_type:1, size:1, dendrite_id: 1}  }, 
		    {$group : {_id: "$dendrite_id", size: {$sum : "$size"}} }, 
		    {$project : { name: "$_id", size:1 , _id: 0}}];

    var basal_pipeline = apical_pipeline.slice();
    basal_pipeline[0] = {$match: {dendrite_type:"basal"}};

    return [ apical_pipeline, basal_pipeline];
}

function groupBySpine() {


    var apical_pipeline = [{$match: {dendrite_type:"apical"}} ,
			   {$project: {dendrite_type:1, size:1, dendrite_id: 1, spine_id:1}  }, 
			   {$group : {_id: "$dendrite_id", 
				      children: {$addToSet: {name: "$spine_id", size: "$size"}} }}, 
			   {$project : { name: "$_id", children:1 , _id: 0}}];

    var basal_pipeline = apical_pipeline.slice();
    basal_pipeline[0] = {$match: {dendrite_type:"basal"}};

    return [ apical_pipeline, basal_pipeline];
}
