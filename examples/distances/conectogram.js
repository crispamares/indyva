/*
 * data = [{conections: [], nodes: []}, ...]
 */

function conectogramChart() {
  var margin = {top: 0, right: 0, bottom: 0, left: 0},
      width = 940,
      height = 500,
      thresholds = [-Infinity, Infinity],
      showText = false;
	  

  var angle = d3.scale.linear(),
      opacity = d3.scale.pow(),
      radialLine = d3.svg.line.radial();

  function chart(selection) {
      selection.each(function(data) {

	  var w = width - margin.left - margin.right;
	  var h = height - margin.top - margin.bottom;
	  var radious = w * .5 * .9;
			 
	  var angle = d3.scale.linear()
	      .domain([0, data.nodes.length])
	      .range([0, 360]);

	  var opacity = d3.scale.pow()
	      .domain([thresholds[0], thresholds[1]])
	      .range([1, 0]);

	  radialLine.interpolate("bundle")
		  .tension(.85)
		  .radius(function(d) { return radious; })
		  .angle(function(d) { return (d.a -90 )/ 180 * Math.PI; });


	  var nodes = _.map(d3.range(0,data.nodes.length), function(d){return {a:angle(d), n:data.nodes[d], i:d};});
	  var links = [];

	  for (var i=0; i < data.nodes.length; i++) {    
	      var j = i;
	      for (; j < data.nodes.length; j++) {
		  var distance = _visit(data.conections, data.nodes.length, i, j);

		  if (distance && distance <= thresholds[1]  && distance >= thresholds[0])
		      links.push([nodes[i], nodes[j]]);
	      }
	  }

	  // Select the svg element, if it exists.
	  var svg = d3.select(this).selectAll("svg").data([data]);

	  // Otherwise, create the skeletal chart.
	  var gEnter = svg.enter().append("svg").append("g");
	  gEnter.append("g").attr("class", "conectogram");

	  // Update the outer dimensions.
	  svg .attr("width", width)
	      .attr("height", height);

          // Update the inner dimensions.
	  var g = svg.select("g")
		  .attr("transform", "translate(" + w/2 + "," + h/2 + ")");

	  var node = g.selectAll("g.node")
	      .data(nodes);
	  node.enter().append("svg:g")
	      .attr("class", "node")
	      .attr("transform", function(d) { return "rotate(" + (d.a - 90) + ")translate(" + radious + ")"; });
	  node.exit().remove();

	if (showText) {
	  node.selectAll('text')
	      .data(function(d){return[d];})
	  .enter().append("svg:text")
	  .attr("dx", function(d) { return d.a < 180 ? 8 : -8; })
	  .attr("dy", ".31em")
	  .attr("text-anchor", function(d) { return d.a < 180 ? "start" : "end"; })
	  .attr("transform", function(d) { return d.a < 180 ? null : "rotate(180)"; })
	  .text(function(d) { return d.n; });
	    
	}

	  node.selectAll('circle')
	      .data(function(d){return[d];})
	      .enter().append("svg:circle")
	      .attr("cx", 0)
	      .attr("cy", 0)
	      .attr("r", 3);	

         var lines = g.selectAll("path.link")
	     .data(links, function(d){return ""+d[0].i+""+d[1].i;});

	 lines.enter().append("svg:path")
	     .attr("class", "link")
	     .attr("opacity", 0.7)
	     .attr("d", radialLine);
/*	     .attr("opacity", function(d){
		       var i = d[0].i;
		       var j = d[1].i;
		       return opacity(_visit(data.conections, i, j));});
*/
         lines.exit().remove();


    });
    
  }

  /**
   * To access the distance vector
   * http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.squareform.html
   */
  function _visit(v, d, i, j) {
      return v[((d * (d-1)) / 2) - (((d-i) * (d-i-1)) / 2) + (j-i-1)];
  }


  function _visit_old(v, d, i, j) {
      return v[_choose(d) - _choose(d-i) + (j-i-1)];
  }

  function _choose(d) {
      return (d * (d-1)) / 2;
  }

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin = _;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.thresholds = function(_) {
    if (!arguments.length) return thresholds;
    thresholds = _;
    return chart;
  };

  chart.showText = function(_) {
    if (!arguments.length) return showText;
    showText = _;
    return chart;
  };

  return chart;
}
