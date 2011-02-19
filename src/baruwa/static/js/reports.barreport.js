// 
// Baruwa - Web 2.0 MailScanner front-end.
// Copyright (C) 2010  Andrew Colin Kissa <andrew@topdog.za.net>
// 
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//
// vim: ai ts=4 sts=4 et sw=4
//
dojo.require("dojox.charting.Chart2D");

//functions
function build_rows(build_array){
	var rows = [];
	var count = 0;
	var c = 'LightBlue_div'
	dojo.forEach(build_array, function(item, i){
	    if (c == 'LightBlue_div') {
	        c = 'LightGray_div';
	    }else{
	        c = 'LightBlue_div';
	    };
		rows[count++] = '<div class="'+c+'">';
		rows[count++] = '<div class="SA_score">'+item.score+'</div>';
		rows[count++] = '<div class="SA_count">'+item.count+'</div>';
		rows[count++] = '</div>';
	});
	return rows.join('');
}

function process_response(data){
    var spinner = dojo.byId("my-spinner");
	spinner.innerHTML = 'Processing...........';
	if (data.success == true) {
		url = window.location.pathname;
		var links = build_filters(data.active_filters);
		dojo.empty("fhl");
		if (links != "") {
		    dojo.place(links,"fhl","last");
		    dojo.removeClass("filterrow","hide");
		}else{
		    dojo.addClass("filterrow","hide");
		};
		dojo.query("#fhl a").onclick(function(e){
		    remove_filter(e,this);
		});
		dojo.xhrGet({
			url:url,
			handleAs:"json",
			load:function(response){
				dojo.empty("graphrows");
				var rows = build_rows(response.items);
				dojo.place(rows,"graphrows","last");
				chart.removeAxis("x");
				var l = [];
				var c = 1;
				for (var i=0; i < response.pie_data.scores.length; i++) {
				    l[i] =  {value:c,text:response.pie_data.scores[i]};
				    c++;
				};
				chart.addAxis("x",{labels: l,majorTickStep:10});
				chart.updateSeries("SA scores",response.pie_data.count,{stroke: {color: "black"}, fill: "blue"});
				chart.render();
				spinner.innerHTML = '';
            	dojo.style('my-spinner','display','none');
            	dojo.attr("filter_form_submit", {'value':'Add'});
            	dojo.removeAttr('filter_form_submit','disabled');
            	window.scrollTo(0,0);
			}
		});
	}else{
		dojo.destroy('filter-error');
		dojo.create('div',{'id':"filter-error",'innerHTML':data.errors+'<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>'},'afform','before');
		var timeout = setTimeout(function(){dojo.destroy('filter-error');},15050);
		dojo.query("#dismiss a").onclick(function(){clearTimeout(timeout); dojo.destroy('filter-error');});
		spinner.innerHTML = '';
    	dojo.style('my-spinner','display','none');
    	dojo.attr("filter_form_submit", {'value':'Add'});
    	dojo.removeAttr('filter_form_submit','disabled');
	};
}

dojo.addOnLoad(function(){
    init_form();
    //bind to form submit
    dojo.query("#filter-form").onsubmit(function(e){
    	e.preventDefault();
    	dojo.attr("filter_form_submit", {'disabled':'disabled','value':gettext('Loading')});
    	dojo.style('my-spinner','display','block');
    	dojo.destroy('filter-error');
    	dojo.xhrPost({
    		form:"filter-form",
    		handleAs:"json",
    		load:function(data){process_response(data);},
    		headers: {"X-CSRFToken": getCookie('csrftoken')}
    	});
    });
    dojo.query("#fhl a").onclick(function(e){
        remove_filter(e,this);
    });
    //init chart and render
	chart = new dojox.charting.Chart2D("chart");
	chart.addPlot("default", {type: "ClusteredColumns",gap:1});
	chart.addAxis("x",{labels: labels,majorTickStep:10});
	chart.addAxis("y", {vertical: true});
	chart.addSeries("SA scores", sa_scores,{stroke: {color: "black"}, fill: "blue"});
	chart.render();	
});