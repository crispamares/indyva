
define(
["when","WsRpc", "vega", "hub"]
,
function () {
    var hub = require('hub');

    var treemapView = function(container) {
	// Subscribe to 'r:'
	// Subscribe to dynamics
	// Setter Data from a table
	this.container = container;
    };

    treemapView.prototype.render = function() {
	var self = this;
	var container = this.container;
	var spec = getTreemapSpec(970, 500, this.data);
	vg.parse.spec(spec, function(chart) {
			  self.view = chart({el:container});
			  self.view.on("click", function(event, item) { 
					   console.log(item.datum.data);
					   hub.instance().publish('spine_selected', item.datum.data);
				       })
			      .update(); 
		      });
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