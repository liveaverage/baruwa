dojo.require("dojox.charting.Chart2D");dojo.require("dojox.charting.plot2d.Pie");dojo.require("dojox.charting.action2d.Highlight");dojo.require("dojox.charting.action2d.MoveSlice");dojo.require("dojox.charting.action2d.Tooltip");dojo.require("dojox.charting.themes.Tufte");function build_rows(a){var d=[];var b=0;var e=1;dojo.forEach(a,function(f,c){if(f.from_address){address=f.from_address}if(f.to_address){address=f.to_address}if(f.from_domain){address=f.from_domain}if(f.site__category){address=f.site__category}if(f.site__site){address=f.site__site}if(f.virusname){address=f.virusname}if(f.bytes){address=f.bytes}if(f.ip__hostname){address=f.ip__hostname}if(f.user__authuser){address=f.user__authuser}if(f.query){address=f.query}d[b++]='<div class="graph_row">';d[b++]='<div class="row_hash">'+e+".</div>";d[b++]='<div class="row_address">';d[b++]='<div class="pie_'+e+' pie"></div>&nbsp;';d[b++]=" "+address+"</div>";d[b++]='<div class="row_count">'+f.num_count+"</div>";d[b++]='<div class="row_volume">'+filesizeformat(f.total_size)+"</div>";d[b++]="</div>";e++});return d.join("")}function process_response(c){var d=dojo.byId("my-spinner");d.innerHTML=gettext("Processing...........");if(c.success==true){url=window.location.pathname;var a=build_filters(c.active_filters);dojo.empty("fhl");if(a!=""){dojo.place(a,"fhl","last");dojo.removeClass("filterrow","hide")}else{dojo.addClass("filterrow","hide")}dojo.query("#fhl a").onclick(function(f){remove_filter(f,this)});dojo.xhrGet({url:url,handleAs:"json",load:function(e){dojo.empty("graphrows");var f=build_rows(e.items);dojo.place(f,"graphrows","last");chart.updateSeries("Series A",e.pie_data);chart.render();d.innerHTML="";dojo.style("my-spinner","display","none");dojo.attr("filter_form_submit",{value:gettext("Add")});dojo.removeAttr("filter_form_submit","disabled")}})}else{dojo.destroy("filter-error");dojo.create("div",{id:"filter-error",innerHTML:c.errors+'<div id="dismiss"><a href="#">'+gettext("Dismiss")+"</a></div>"},"afform","before");var b=setTimeout(function(){dojo.destroy("filter-error")},15050);dojo.query("#dismiss a").onclick(function(){clearTimeout(b);dojo.destroy("filter-error")});d.innerHTML="";dojo.style("my-spinner","display","none");dojo.attr("filter_form_submit",{value:gettext("Add")});dojo.removeAttr("filter_form_submit","disabled")}}dojo.addOnLoad(function(){init_form(is_web);dojo.query("#filter-form").onsubmit(function(f){f.preventDefault();dojo.attr("filter_form_submit",{disabled:"disabled",value:gettext("Loading")});dojo.style("my-spinner","display","block");dojo.destroy("filter-error");dojo.xhrPost({form:"filter-form",handleAs:"json",load:function(e){process_response(e)},headers:{"X-CSRFToken":getCookie("csrftoken")}})});dojo.query("#fhl a").onclick(function(f){remove_filter(f,this)});var a=dojox.charting;chart=new a.Chart2D("chart");chart.setTheme(a.themes.Tufte).addPlot("default",{type:"Pie",font:"normal normal 8pt Tahoma",fontColor:"black",labelOffset:-30,radius:80});chart.addSeries("Series A",json_data);var d=new a.action2d.MoveSlice(chart,"default");var c=new a.action2d.Highlight(chart,"default");var b=new a.action2d.Tooltip(chart,"default");chart.render()});