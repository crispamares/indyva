require.config({
    baseUrl: 'js',
    paths: {
        jquery: 'vendor/jquery.min',
	bootstrap: 'vendor/bootstrap.min',
	when: 'vendor/when',
	d3: 'vendor/d3.v3.min',
	vega: 'vendor/vega',
	lodash: 'vendor/lodash.min'
    }
});


requirejs(['jquery', 
	   'lodash',
	   'when', 
	   'bootstrap', 
	   'WsRpc',
	   'hub',
	   'd3',
	   'vega',
	   'treemap',
	   'comboSelector'], 

function($, _, when, bootstrap, WsRpc, Hub, d3, vega ) {
    console.log('running');

    rpc = new WsRpc();
    rpc.install();

    hub = new Hub();
    hub.install();

    var treemap = require("treemap");
    var view = new treemap("#overview"); 
    hub.subscribe('comboChanged', 
	    function(topic, msg) { 
		console.log(topic);
		drawTreemap(when, rpc, view, msg);});

    drawTreemap(when, rpc, view, "size");

    var comboSelector = require("comboSelector");
    var menu = new comboSelector('#menu');
    menu.update();

});

function drawTreemap(when, rpc, view, column) {
    when.map( groupBySpine(column),
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
}

function groupByDendriteId(column) {
    column = column || 'size';

    var apical_pipeline = [{$match: {dendrite_type:"apical"}},
		    {$project: {dendrite_type:1, size:1, dendrite_id: 1}  }, 
		    {$group : {_id: "$dendrite_id", size: {$sum : "$size"}} }, 
		    {$project : { name: "$_id", size:1 , _id: 0}}];

    var basal_pipeline = apical_pipeline.slice();
    basal_pipeline[0] = {$match: {dendrite_type:"basal"}};

    return [ apical_pipeline, basal_pipeline];
}

function groupBySpine(column) {
    column = column || 'size';

    var project1 = {$project: {dendrite_type:1, dendrite_id: 1, spine_id:1}};
    project1.$project[column] = 1;

    var group = {$group : {_id: "$dendrite_id", 
		 children: {$addToSet: {name: "$spine_id", size:'$'+column}} }};

    var apical_pipeline = [{$match: {dendrite_type:"apical"}} ,
			   project1,
			   group,
			   {$project : { name: "$_id", children:1 , _id: 0}}];

    var basal_pipeline = apical_pipeline.slice();
    basal_pipeline[0] = {$match: {dendrite_type:"basal"}};

    return [ apical_pipeline, basal_pipeline];
}
