define(['lodash', 'jquery', 'WsRpc', 'hub', 'd3'],
function() {

    var hub = require('hub');

    function SelectionList(container, dselect) {
	this.container = $(container);
	this.dselect = dselect;
	this.items = [{name:"PACOOO"}, {name:"length"}, {name:"angle"}];

	var template = _.template('<div class="panel panel-default">'
			   + '  <div class="panel-heading">'
			   + '    <h3 class="panel-title">Selections</h3>'
			   + '  </div>'
			   + '  <div class="panel-body">'
			   + '    <ul class="list-group">'
			   + '    </ul>'			   
			   + '  </div>'
			   + '</div>');
	var html = template({items: this.items});
	this.container.append(html);

    }
    
    SelectionList.prototype.update =  function() {
	
	var ul = d3.select(this.container.selector)
	    .select('ul').selectAll('li').data(this.items, function(d){return d.name;});

	ul.enter()
	    .append('li')
	    .attr("class", "list-group-item")
	    .text(function(d) {return d.name;})
	    .on("click", function(d) {
		hub.instance().publish('spine_selected', d.name);});

	    
	
    };
    
    return SelectionList;
}
);