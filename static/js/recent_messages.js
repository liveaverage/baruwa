
function build_table_from_json(){
    if(! ax_in_progress){
        $.getJSON('/messages/',json2html); 
        $.address.value('?u=');
        $.address.history($.address.baseURL());
        if(auto_refresh){
            clearInterval(auto_refresh);
        }
        setTimeout(build_table_from_json,60000);
    }else{
        alert('Blocking ajax request');
    }
}

function do_table_sort(){
ax_in_progress = false;
theTable = $('#recent').dataTable( {
	"aaSorting": [[ 1, "desc" ]],
	"sDom": 'frt',
	"bPaginate": false,
	"asStripClasses": [],
	"fnRowCallback": format_rows,
	"aoColumns": [{"bSortable": false,"bSearchable": false},null,null,null,null,null,null,{"bSearchable": false}]
});

$("#search-area").ajaxSend(function() {
	$(this).empty();
	$(this).append($("<img/>").attr("src","/static/imgs/loader.gif")).append('&nbsp;Refreshing........');
	ax_error = false;
    ax_in_progress = true;
});

$("#search-area").ajaxStop(function() {
	if(!ax_error){
		$(this).empty();
		var lu = lastupdatetime();
		$(this).append('[last refreshed at '+lu+']');
        ax_in_progress = false;
	}
});

$("#search-area").ajaxError(function(){
	$(this).empty();
	$(this).append('<span class="ajax_error">Error connecting to server. check network!</span>');
	ax_error = true;
    ax_in_progress = false;
    $.address.value('?u=');
    $.address.history($.address.baseURL());
});
//$.ajaxSetup({timeout:2000});
$('a').bind('click',function(event){
    if(ax_in_progress){
        event.preventDefault();
        alert('Refreshing is in progress, please wait for it to complete');
    }else{
        if($(this).attr('href') != '#'){
            ax_in_progress = true;
        }
        $.address.value('?u=');
        $.address.history($.address.baseURL());
    }
});
    $.address.externalChange(function(){ax_in_progress = false;});
}

var auto_refresh = setInterval(build_table_from_json, 60000);
$(document).ready(do_table_sort);
