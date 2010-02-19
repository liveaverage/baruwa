
function build_table_from_json(){
    $.getJSON('/messages/',json2html); 
    clearInterval(auto_refresh);
    setTimeout(build_table_from_json,60000);
}

function do_table_sort(){
	theTable = $('#recent').dataTable( {
	"aaSorting": [[ 1, "desc" ]],
	//"sDom": '<"top-layer"lf><"ajax-table"rt><"bottom-layer"ip',
	"sDom": 'frt',
	"bPaginate": false,
	"asStripClasses": [],
	"fnRowCallback": format_rows,
	"aoColumns": [{"bSortable": false,"bSearchable": false},null,null,null,null,null,null,{"bSearchable": false}]
});

$("#search-area").ajaxSend(function() {
	$(this).empty();
	$(this).append($("<img/>").attr("src","/static/imgs/loader.gif")).append('&nbsp;Refreshing........');
	//$(this).append('<img src="/static/imgs/loader.gif" alt="loading"/>&nbsp;Refreshing........');
	ax_error = false;
});

$("#search-area").ajaxStop(function() {
	if(!ax_error){
		$(this).empty();
		var lu = lastupdatetime();
		$(this).append('[last refreshed at '+lu+']');
	}
});

$("#search-area").ajaxError(function(){
	$(this).empty();
	$(this).append('<span class="ajax_error">Error connecting to server. check network!</span>');
	ax_error = true;
});
//$.ajaxSetup({timeout:2000});
}

var auto_refresh = setInterval(build_table_from_json, 60000);
$(document).ready(do_table_sort);
