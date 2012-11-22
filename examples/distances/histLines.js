function histoLinesChart() {
  var margin = {top: 0, right: 0, bottom: 20, left: 0},
      width = 960,
      height = 500,
      showCircles = true;

  var histogram = d3.layout.histogram(),
      x = d3.scale.ordinal(),
      y = d3.scale.linear(),
      xAxis = d3.svg.axis().scale(x).orient("bottom").tickSize(6, 0),
      line = d3.svg.area();

  function chart(selection) {
    selection.each(function(data) {

      // Compute the histogram.
      data = histogram(data);

      // Update the x-scale.
      x .domain(data.map(function(d) { return d.x; }))
          .rangeRoundBands([0, width - margin.left - margin.right], .1);

      // Update the y-scale.
      y .domain([0, d3.max(data, function(d) { return d.y; })])
          .range([height - margin.top - margin.bottom, 0]);

      // Select the svg element, if it exists.
      var svg = d3.select(this).selectAll("svg").data([data]);

      // Otherwise, create the skeletal chart.
      var gEnter = svg.enter().append("svg").append("g");
      gEnter.append("g").attr("class", "lines");
      gEnter.append("g").attr("class", "circles");
      gEnter.append("g").attr("class", "x axis");

      // Update the outer dimensions.
      svg .attr("width", width)
          .attr("height", height);

      // Update the inner dimensions.
      var g = svg.select("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      line.x(function(d) { return x(d.x); })
	  .y(function(d) { return y(d.y); })
	  .y0(y.range()[0]);

      // Update the lines.
      var lines = svg.select(".lines").selectAll('.line').data([data]);
      lines.enter().append("svg:path");
      lines.exit().remove();
      lines.attr('d', function(d) {return line(d);});

      if (showCircles) {
      // Update the circles.
	  var circle = svg.select(".circles").selectAll(".circle").data(data);
	  circle.enter().append("circle");
	  circle.exit().remove();
	  circle.attr("r", 5)
              .attr("cx", function(d) { return x(d.x); })
              .attr("cy", function(d) { return y(d.y); })
	      .attr('title', function(d) {return String(d.x);})
	      .each( function (p) { $(this).tooltip();});
	  
      }


      // Update the x-axis.
      g.select(".x.axis")
          .attr("transform", "translate(0," + y.range()[0] + ")")
          .call(xAxis);
    });
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

  chart.showCircles = function(_) {
    if (!arguments.length) return showCircles;
    showCircles = _;
    return chart;
  };

  // Expose the histogram's value, range and bins method.
  d3.rebind(chart, histogram, "value", "range", "bins", "frequency");

  // Expose the x-axis' tickFormat method.
  d3.rebind(chart, xAxis, "tickFormat", "ticks");

  // Expose the lines' interpolate method.
  d3.rebind(chart, line, "interpolate");

  return chart;
}