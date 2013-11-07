define(['lodash', 'jquery', 'WsRpc', 'hub'],
function() {

    var hub = require('hub');

    function ComboSelector(container, table, attributeType) {
	this.container = $(container);
	this.options = ["size", "length", "angle"];
    }
    
    ComboSelector.prototype.update =  function() {
	
	var template = _.template('<select class="form-control">'
			   + '<% _.forEach(options, function(option) {%>'
			   + '<option> <%- option  %> </option> <% }) %>'
			   + '</select>');
	var html = template({options: this.options});
	this.container.html(html);

	this.container
	    .find('select')
	    .on('change', function(e) {
		    console.log (e);
		    hub.instance().publish('comboChanged', e.target.value);
		});
    };
    

    return ComboSelector;
}
);