
var DIS = {
    columns: [
	{
	    name: "stack",
	    type: "string"
	},
	{
	    name: "d",
	    type: undefined
	},
	{
	    name: "layer",
	    type: "string"
	}],
    Views: {},
    views: {},
    config: {},
    state: {}
};

d3.json('/data/all_data_distances.json', main);

function main(all_data) {
    window.all_data = all_data;

    var data = distance_by_stack(all_data);
    DIS.ds = new Miso.Dataset({columns: DIS.columns, data: data});

    DIS.config.groupings = [DIS.columns[2], DIS.columns[0]];
    DIS.state.placeOnTop = false;
    DIS.state.interpolate = false;
    DIS.state.currentGrouping = DIS.config.groupings[0].name;

    DIS.views.distancesView = new DIS.Views.DistancesView();
    DIS.views.grouping = new DIS.Views.Grouping();
    DIS.views.place = new DIS.Views.Place();    
    DIS.views.interpolate = new DIS.Views.Interpolate();    
    DIS.views.conectogram = new DIS.Views.ConectogramView();

    DIS.ds.fetch({
	    success: function() {
		// ds.groupBy("layer", ["d"], {method: _.flatten})
		console.log(this);
		DIS.router = new DIS.Router();
		Backbone.history.start();
	    }
	});
    };

function distance_by_stack(all_data) {
    var data = _.map(all_data, function(l, layerK) {
			 return _.map(l, function (s, stackK) {
					  return {stack: stackK, d: s.distances.d, layer: layerK, n: s.distances.i};
							    });
		     });
    return _.flatten(data);
}


DIS.Router = Backbone.Router.extend({
  routes: {
      "":		      "histogram",
      "histogram":	      "histogram",
      "conectogram":          "conectogram"    // #help
  },
  histogram: function() {
      DIS.state.mainView = DIS.views.distancesView;

      DIS.views.conectogram.remove();

      DIS.views.distancesView.render();
      DIS.views.grouping.render();
      DIS.views.place.render();      
      DIS.views.interpolate.render();      

  },
  conectogram: function() {
      DIS.state.mainView = DIS.views.conectogram;

      console.log("conectogram");
      DIS.views.distancesView.remove();
      DIS.views.grouping.remove();
      DIS.views.interpolate.remove();      

      DIS.views.conectogram.render();
      DIS.views.place.render();
  }
});

DIS.Views.DistancesView = Backbone.View.extend({
    el: "div#distances-div",
    template: "script#distances-div",

    initialize: function(args){
	_.bindAll(this);
	this.template  = _.template($(this.template).html());

	args = args || false;

	this.h = args.h || 900;
	this.w = args.w || $(this.el).width();
	this.m = args.m || [7, 30, 18, 10]; // top right bottom left

    },
    _compute_range: function(data) {
	var min = _.reduce(data, function(memo, d) {return Math.min(memo, d3.min(d));}, Infinity);
	var max = _.reduce(data, function(memo, d) {return Math.max(memo, d3.max(d));}, -Infinity);
	return [min, max];
    },
    remove: function() {
	$(this.el).empty();
    },
    render: function() {
	console.log("RENDERING", DIS.state.currentGrouping);
	
//	var data = this.ds.column("d").data;
	var data = DIS.ds.groupBy(DIS.state.currentGrouping, ["d"], {method: _.flatten}).column("d").data;

	var layers = DIS.ds.column('layer').data;
	layers = (DIS.state.currentGrouping == 'layer') ? _.uniq(layers) : layers;

	var range = this._compute_range(data);
	console.log('range', range);
//	data = [data[0]];

	$(this.el).html(this.template());

	this.svg = d3.select(this.el)
	    .select('.chart_container')
	    .append('svg:svg')
	    .attr('width', this.w)
	    .attr('height', this.h)
	    .classed('chart_container', true);
	this.g = this.svg
	    .append("svg:g")
	    .attr("class", "column_g")
	    .attr("transform", "translate(" + this.m[3] + "," + this.m[0] + ")");


	var gridfn = gridLayout()
	    .width(this.w - this.m[1] - this.m[3])
	    .height(this.h - this.m[0] - this.m[2])
	    .count(data.length);	    
	var grid = gridfn();

	if ( DIS.state.placeOnTop) {
	    grid.xSize = gridfn.width();
	    grid.ySize = gridfn.height();
	}
	
	var histogram = histoLinesChart()
	    .margin({top: 20, right: 5, bottom: 5, left: 5})
	    .width(grid.xSize)
	    .height(grid.ySize)
	    .bins(150)
	    .showCircles(false)
	    .range(range)
	    .tickFormat(d3.format(".0f"))
	    .ticks(3)
	    .frequency(true);

	if (DIS.state.interpolate)
	    histogram.interpolate('basis');
	else
	    histogram.interpolate('step-after');
	
	var elem_g = this.g.selectAll('.elem_g').data(data);
	elem_g.enter()
	    .append("svg:g")
	    .attr("class", function (d,i) {return 'Layer'+layers[i];})
	    .classed("elem_g", true)
	    .attr("transform", function(d, i) {return (! DIS.state.placeOnTop) 
					       ? "translate(" + grid.x(i) + "," + grid.y(i) + ")" 
					       : "translate( 0, 0)";})
	    .call(histogram);
	elem_g.exit()
	    .remove();
		    

    }
});




DIS.Views.ConectogramView = Backbone.View.extend({
    el: "div#distances-div",
    template: "script#distances-div",

    initialize: function(args){
	_.bindAll(this);
	this.template  = _.template($(this.template).html());

	args = args || false;

	this.h = args.h || 900;
	this.w = args.w || $(this.el).width();
	this.m = args.m || [7, 30, 18, 10]; // top right bottom left

    },
    _compute_range: function(data) {
	var min = _.reduce(data, function(memo, d) {return Math.min(memo, d3.min(d));}, Infinity);
	var max = _.reduce(data, function(memo, d) {return Math.max(memo, d3.max(d));}, -Infinity);
	return [min, max];
    },
    remove: function() {
	$(this.el).empty();
    },
    render: function() {
	console.log("RENDERING ConectogramView");
	
	data = [];
	DIS.ds.each(function(row){data.push({conections:row.d, nodes: row.n});});
	var layers = DIS.ds.column('layer').data;

//	var range = this._compute_range(data);
	//data = [data[0]];

	$(this.el).html(this.template());

	this.svg = d3.select(this.el)
	    .select('.chart_container')
	    .append('svg:svg')
	    .attr('width', this.w)
	    .attr('height', this.h)
	    .classed('chart_container', true);
	this.g = this.svg
	    .append("svg:g")
	    .attr("class", "column_g")
	    .attr("transform", "translate(" + this.m[3] + "," + this.m[0] + ")");

	var gridfn = gridLayout()
	    .width(this.w - this.m[1] - this.m[3])
	    .height(this.h - this.m[0] - this.m[2])
	    .count(data.length);	    
	var grid = gridfn();

	if ( DIS.state.placeOnTop) {
	    grid.xSize = gridfn.width();
	    grid.ySize = gridfn.height();
	}
	
	var conectogram = conectogramChart()
	    .margin({top: 5, right: 5, bottom: 5, left: 5})
	    .width(grid.xSize)
	    .height(grid.ySize)
	    .thresholds([4600, 4700]);

	var elem_g = this.g.selectAll('.elem_g').data(data);
	elem_g.enter()
	    .append("svg:g")
	    .attr("class", function (d,i) {return 'Layer'+layers[i];})
	    .classed("elem_g", true)
	    .attr("transform", function(d, i) {return (! DIS.state.placeOnTop) 
					       ? "translate(" + grid.x(i) + "," + grid.y(i) + ")" 
					       : "translate( 0, 0)";})
	    .call(conectogram);
	elem_g.exit()
	    .remove();
		    

    }
});


/**
* Represents a dropdown box with a list of grouping options.
*/
DIS.Views.Grouping = Backbone.View.extend({

  el : "#groupby",
  template : 'script#grouping',
  events : {
    "change" : "onChange"
  },

  initialize : function(options) {
    options = options || {};
    this.groupings = options.groupings || DIS.config.groupings;
    this.template = _.template($(this.template).html());

    console.log('groupings', this.groupings, DIS.config.groupings, DIS);

    this.$el = $(this.el);
    //this.setElement($(this.el));
  },
  render : function () {
    this.$el.parent().show();
    this.$el.html(this.template({ columns : this.groupings }));
    return this;
  },

  // Whenever the dropdown option changes, re-render
  // the chart.
  onChange : function(e) {
    DIS.state.currentGrouping = $("option:selected", e.target).val();
    DIS.views.distancesView.render();
  },
  remove: function() {
    this.$el.parent().hide();
  }
});


/**
* Represents a toggle button controling the placeOnTop
*/
DIS.Views.Place = Backbone.View.extend({

  el : "#place",
  events : {
    "click" : "onChange"
  },

  initialize : function(options) {
    options = options || {};
 //   this.template = _.template($(this.template).html());

    this.$el = $(this.el);
    //this.setElement($(this.el));
  },

  render : function () {
    this.$el.parent().show();
//    this.$el.html(this.template({ columns : this.groupings }));
    return this;
  },

  // Whenever the dropdown option changes, re-render
  // the chart.
  onChange : function(e) {
      var checkable = e.target;
      DIS.state.placeOnTop = checkable.checked;
      DIS.state.mainView.render();
  },
  remove: function() {
    this.$el.parent().hide();
  }

});


/**
* Represents a toggle button controling the interpolation
*/
DIS.Views.Interpolate = Backbone.View.extend({

  el : "#basis",
  events : {
    "click" : "onChange"
  },

  initialize : function(options) {
    options = options || {};
 //   this.template = _.template($(this.template).html());

    this.$el = $(this.el);
    //this.setElement($(this.el));
  },

  render : function () {
    this.$el.parent().show();
//    this.$el.html(this.template({ columns : this.groupings }));
    return this;
  },

  // Whenever the dropdown option changes, re-render
  // the chart.
  onChange : function(e) {
      var checkable = e.target;
      DIS.state.interpolate = checkable.checked;
      DIS.views.distancesView.render();
  },
  remove: function() {
    this.$el.parent().hide();
  }

});




function gridLayout() {
    var margin = {top: 0, right: 0, bottom: 0, left: 0},
      width = 960,
      height = 500;

    var count = 10,
	x = d3.scale.linear(),
	y = d3.scale.linear();

    function gridLayout() {
	var xCount = Math.ceil(Math.sqrt(count)),
	    yCount = xCount,
	    xSize = (width - margin.right - margin.left) / xCount,
	    ySize = (height - margin.top - margin.bottom) / yCount;
	console.log(count, xCount, yCount, width, height);

	x.domain([0, xCount]).range([0, width - margin.right - margin.left]);
	y.domain([0, yCount]).range([0, height - margin.top - margin.bottom]);

	return {x: function(i) {return x(i % xCount) ;},
		y: function(i) {return y(Math.floor(i / xCount)) ;},
		xSize: xSize,
	        ySize: ySize};
    }

    gridLayout.count = function(_) {
	if (!arguments.length) return count;
	count = _;
	return gridLayout;
    };

    gridLayout.margin = function(_) {
	if (!arguments.length) return margin;
	margin = _;
	return gridLayout;
    };

    gridLayout.width = function(_) {
	if (!arguments.length) return width;
	width = _;
	return gridLayout;
    };

    gridLayout.height = function(_) {
	if (!arguments.length) return height;
	height = _;
	return gridLayout;
    };

    return gridLayout;
}