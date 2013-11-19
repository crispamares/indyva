
define(
["when","WsRpc", "d3", "hub", "jquery"]
,
function () {
    var hub = require('hub');

    var treemapView = function(container) {
	// Subscribe to 'r:'
	// Subscribe to dynamics
	// Setter Data from a table
	this.container = container;

	var width = 960,
	    height = 500;

	var color = d3.scale.category20c();

	var treemap = d3.layout.treemap()
	    .size([width, height])
	    .padding(4)
	    .value(function(d) { return d.size; });

	var div = d3.select(container).append("div")
	    .style("position", "relative")
	    .style("width", width + "px")
	    .style("height", height + "px");

	this.render = function() {

	    var nodes = div.selectAll(".node")
		.data(treemap.nodes(this.data));

	    nodes.enter().append("div")
		.attr("class", "node")
		.style("background", function(d) { return d.children ? color(d.name) : null; });

	    nodes
		.style("left", function(d) { return d.x + "px"; })
		.style("top", function(d) { return d.y + "px"; });

	    var leaves = nodes.filter(function(d){return ! Boolean(d.children);});
	    var parents = nodes.filter(function(d){return Boolean(d.children);});
	    parents
		.style("width", function(d) { return Math.max(0, d.dx - 1) + "px"; })
		.style("height", function(d) { return Math.max(0, d.dy - 1) + "px"; });

	    leaves		
		.classed("leaf", true)
		.style("left", function(d) { return Math.max(0, d.x - 1) + "px"; })
		.style("top", function(d) { return Math.max(0, d.y - 1) + "px"; })
		.style("width", function(d) { return d.dx + 1 + "px"; })
		.style("height", function(d) { return d.dy + 1 + "px"; })
		.on("click", function(d) {
			hub.instance().publish('spine_selected', d.name);
		    });




		//.text(function(d) { return d.children ? null : d.name; });

	};

    };
    
    treemapView.prototype.update = function() {
	if (this.view){
	    console.log('update', this.view.width());
	    this.view = 
	    this.view.update();
	}
	else
	    this.render();
    };

    treemapView.prototype.setData = function(data) {
	this.data = data;
/*	if (this.view) {
	    var vg_data = [{
		    "name": "tree",
		    "values": data,
		    "format": {"type": "treejson"},
		    "transform": [
			{"type": "treemap", "value": "data.size"}
		    ]
		}];
		gvalues = data;
		gdata = vg_data;
		gview = this.view;
	    console.log('data', this.data);
	    this.view.data(vg.parse.data(vg_data).flow);
	}
*/    };


    function getTreemapSpec(width, height, data) {

	var treemap_spec = {
	    "name": "treemap",
	    "width": width,
	    "height": height,
	    "padding": 2.5,
	    "data": [
		{
		    "name": "tree",
		    "values": data,
		    "format": {"type": "treejson"},
		    "transform": [
			{"type": "treemap", "value": "data.size"}
		    ]
		}
	    ],
	    "scales": [
		{
		    "name": "color",
		    "type": "ordinal",
		    "range": [
			"#3182bd", "#6baed6", "#9ecae1", "#c6dbef", "#e6550d",
			"#fd8d3c", "#fdae6b", "#fdd0a2", "#31a354", "#74c476",
			"#a1d99b", "#c7e9c0", "#756bb1", "#9e9ac8", "#bcbddc",
			"#dadaeb", "#636363", "#969696", "#bdbdbd", "#d9d9d9"
		    ]
		},
		{
		    "name": "size",
		    "type": "ordinal",
		    "domain": [0, 1, 2, 3],
		    "range": [256, 28, 20, 14]
		},
		{
		    "name": "opacity",
		    "type": "ordinal",
		    "domain": [0, 1, 2, 3],
		    "range": [0.15, 0.5, 0.8, 1.0]
		}
	    ],
	    "marks": [
		{
		    "type": "rect",
		    "from": {
			"data": "tree",
			"transform": [{"type":"filter", "test":"d.values"}]
		    },
		    "interactive": false,
		    "properties": {
			"enter": {
			    "x": {"field": "x"},
			    "y": {"field": "y"},
			    "width": {"field": "width"},
			    "height": {"field": "height"},
			    "fill": {"scale": "color", "field": "data.name"}
			}
		    }
		},
		{
		    "type": "rect",
		    "from": {
			"data": "tree",
			"transform": [{"type":"filter", "test":"!d.values"}]
		    },
		    "properties": {
			"enter": {
			    "x": {"field": "x"},
			    "y": {"field": "y"},
			    "width": {"field": "width"},
			    "height": {"field": "height"},
			    "stroke": {"value": "#fff"}
			},
			"update": {
			    "fill": {"value": "rgba(0,0,0,0)"}
			},
			"hover": {
			    "fill": {"value": "red"}
			}
		    }
		}
/*		,{
		    "type": "text",
		    "from": {
			"data": "tree",
			"transform": [{"type":"filter", "test":"d.values"}]
		    },
		    "interactive": false,
		    "properties": {
			"enter": {
			    "x": {"field": "x"},
			    "y": {"field": "y"},
			    "dx": {"field": "width", "mult": 0.5},
			    "dy": {"field": "height", "mult": 0.5},
			    "font": {"value": "Helvetica Neue"},
			    "fontSize": {"scale": "size", "field": "depth"},
			    "align": {"value": "center"},
			    "baseline": {"value": "middle"},
			    "fill": {"value": "#000"},
			    "fillOpacity": {"scale": "opacity", "field": "depth"},
			    "text": {"field": "data.name"}
			}
		    }
		}
*/
	    ]
	};
	return treemap_spec;
    }
return treemapView;
}
);