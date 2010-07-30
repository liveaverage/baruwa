dojo.require("dojox.charting.Chart2D");
dojo.require("dojox.charting.plot2d.Pie");
dojo.require("dojox.charting.action2d.Highlight");
dojo.require("dojox.charting.action2d.MoveSlice");
dojo.require("dojox.charting.action2d.Tooltip");
dojo.require("dojox.charting.themes.Tufte");
dojo.addOnLoad(function() {
dojo.byId("fhl").style.display = "none";
dojo.create("a",{href:"#",innerHTML:"&darr;&nbsp;Show filters&nbsp;",id:"filter-toggle"},"fhl","before");
dojo.connect(dojo.byId("filter-toggle"),"onclick",function(e){
        e.preventDefault();
        em = dojo.byId("fhl");
        if(em.style.display == "inline"){
            em.style.display = "none";
            dojo.byId("filter-toggle").innerHTML = "&darr;&nbsp;Show filters&nbsp;";
        }else{
            em.style.display = "inline";
            dojo.byId("filter-toggle").innerHTML = "&uarr;&nbsp;Hide filters&nbsp;";
        }
});

//functions
function build_rows(build_array){
	var rows = [];
	var count = 0;
	var c = 1;
	dojo.forEach(build_array, function(item, i){
		if (item.from_address) {
			address = item.from_address;
		};
		if (item.to_address) {
			address = item.to_address;
		};
		if (item.from_domain) {
			address = item.from_domain;
		};
		if (item.to_domain) {
			address = item.to_domain;
		};
		rows[count++] = '<div class="graph_row">';
		rows[count++] = '<div class="row_hash">'+c+'.</div>';
		rows[count++] = '<div class="row_address">';
		rows[count++] = '<div class="pie_'+c+' pie"></div>&nbsp;';
		rows[count++] = ''+address+'</div>';
		rows[count++] = '<div class="row_count">'+item.num_count+'</div>';
		rows[count++] = '<div class="row_volume">'+filesizeformat(item.size)+'</div>';
		rows[count++] = '</div>';
		c++;
	});
	return rows.join('');
}

function build_filters(filter_array){
	var links = [];
	var count = 0;
	dojo.forEach(filter_array, function(item, i){
		links[count++] = '<a href="">'+item.filter_field+' '+item.filter_by+' '+item.filter_value+'</a>';
	});
	return links.join(',');
}

//form initialization
bool_fields = ["spam","highspam","saspam","rblspam","whitelisted","blacklisted","virusinfected","nameinfected","otherinfected","isquarantined"];
num_fields = ["size","sascore"];
text_fields = ["id","from_address","from_domain","to_address","to_domain","subject","clientip","spamreport","headers"];
time_fields = ["date","time"];
num_values = [{'value':1,'opt':'is equal to'},{'value':2,'opt':'is not equal to'},{'value':3,'opt':'is greater than'},{'value':4,'opt':'is less than'}];
text_values = [{'value':1,'opt':'is equal to'},{'value':2,'opt':'is not equal to'},{'value':9,'opt':'is null'},{'value':10,'opt':'is not null'},{'value':5,'opt':'contains'},{'value':6,'opt':'does not contain'},{'value':7,'opt':'matches regex'},{'value':8,'opt':'does not match regex'}];
time_values = [{'value':1,'opt':'is equal to'},{'value':2,'opt':'is not equal to'},{'value':3,'opt':'is greater than'},{'value':4,'opt':'is less than'}];
bool_values = [{'value':11,'opt':'is true'},{'value':12,'opt':'is false'}];
dojo.place('<option value="0" selected="0">Please select</option>', "id_filtered_field", 'first');
dojo.attr('id_filtered_value', 'disabled', 'disabled');
select_field = dojo.query("#id_filtered_field");
select_field.onchange(function(e){
	var value_to_check = dojo.byId("id_filtered_field").value;
	if (dojo.indexOf(bool_fields, value_to_check) != -1) {
		dojo.empty("id_filtered_by");
		dojo.forEach(bool_values, function(item, i){
			dojo.create("option",{value:item.value,innerHTML:item.opt},'id_filtered_by','last');
		});
		dojo.attr('id_filtered_value', 'disabled', 'disabled');
		dojo.byId('id_filtered_value').value = '';
	};
	if (dojo.indexOf(num_fields, value_to_check) != -1) {
		dojo.empty("id_filtered_by");
		dojo.forEach(num_values, function(item, i){
			dojo.create("option",{value:item.value,innerHTML:item.opt},'id_filtered_by','last');
		});
		dojo.removeAttr('id_filtered_value','disabled');
		dojo.byId('id_filtered_value').value = '';
	};
	if (dojo.indexOf(text_fields, value_to_check) != -1) {
		dojo.empty("id_filtered_by");
		dojo.forEach(text_values, function(item, i){
			dojo.create("option",{value:item.value,innerHTML:item.opt},'id_filtered_by','last');
		});
		dojo.removeAttr('id_filtered_value','disabled');
		dojo.byId('id_filtered_value').value = '';
	};
	if (dojo.indexOf(time_fields, value_to_check) != -1) {
		dojo.empty("id_filtered_by");
		dojo.forEach(time_values, function(item, i){
			dojo.create("option",{value:item.value,innerHTML:item.opt},'id_filtered_by','last');
		});
		dojo.removeAttr('id_filtered_value','disabled');
		if (value_to_check == 'time') {
			dojo.byId('id_filtered_value').value = 'HH:MM';
		};
		if (value_to_check == 'date') {
			dojo.byId('id_filtered_value').value = 'YYYY-MM-DD';
		};
	};
});

dojo.query("#filter-form").onsubmit(function(e){
	e.preventDefault();
	dojo.attr("filter_form_submit", {'disabled':'disabled','value':'Loading'});
	var spinner = dojo.byId("my-spinner");
	spinner.innerHTML = 'Processing...........';
	dojo.style('my-spinner','display','block');
	dojo.destroy('filter-error');
	dojo.xhrPost({
		form:"filter-form",
		handleAs:"json",
		load:function(data){
			if (data.success == true) {
				url = window.location.pathname;
				var links = build_filters(data.active_filters);
				dojo.empty("fhl");
				dojo.place(links,"fhl","last");
				dojo.xhrGet({
					url:url,
					handleAs:"json",
					load:function(response){
						dojo.empty("graphrows");
						var rows = build_rows(response.items);
						dojo.place(rows,"graphrows","last");
						pie_graph.updateSeries("Series A", response.pie_data);
						pie_graph.render();
						
					}
				});
			}else{
				dojo.destroy('filter-error');
				dojo.create('div',{'id':"filter-error",'innerHTML':data.errors},'afform','before');
			};
			spinner.innerHTML = '';
			dojo.style('my-spinner','display','none');
			dojo.attr("filter_form_submit", {'value':'Add'});
			dojo.removeAttr('filter_form_submit','disabled');
		}
	});
});
	
//pie chart initialization
	var dc = dojox.charting;
	pie_graph = new dc.Chart2D("pie_graph");
	pie_graph.setTheme(dc.themes.Tufte).addPlot("default", {
	type: "Pie",
	font: "normal normal 8pt Tahoma",
	fontColor: "black",
	labelOffset: -30,
	radius: 80
	});
	pie_graph.addSeries("Series A", json_data);
	var anim_a = new dc.action2d.MoveSlice(pie_graph, "default");
	var anim_b = new dc.action2d.Highlight(pie_graph, "default");
	var anim_c = new dc.action2d.Tooltip(pie_graph, "default");
	pie_graph.render();
	
});