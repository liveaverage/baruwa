function prevent_interupt_refresh(event){
    if(ax_in_progress){
        event.preventDefault();
        $("#in-progress").html("Refreshing is in progress, please wait for it to complete").show('fast');
    }
}

function build_table_from_json(){
    if(! ax_in_progress){
        $.getJSON('/messages/',json2html); 
        if(auto_refresh){
            clearInterval(auto_refresh);
        }
        $("#recent a").bind('click',prevent_interupt_refresh);
        setTimeout(build_table_from_json,60000);
    }
}

function do_table_sort(){
    ax_in_progress = false;
    $("#search-area").ajaxSend(function(){
	    $(this).empty();
	    $(this).append($("<img/>").attr("src","/static/imgs/loader.gif")).append('&nbsp;Refreshing........');
	    ax_error = false;
        ax_in_progress = true;
    })
    .ajaxStop(function() {
	    if(!ax_error){
		    $(this).empty();
		    var lu = lastupdatetime();
		    $(this).append('[last refreshed at '+lu+']');
            ax_in_progress = false;
            if($("#in-progress").is(':visible')){
                $("#in-progress").hide();
            }
	    }
    })
    .ajaxError(function(){
	    $(this).empty();
	    $(this).append('<span class="ajax_error">Error connecting to server. check network!</span>');
	    ax_error = true;
        ax_in_progress = false;
        if($("#in-progress").is(':visible')){
            $("#in-progress").hide();
        }
        setTimeout(build_table_from_json,60000);
    });
    $('a').bind('click',prevent_interupt_refresh);
}

var auto_refresh = setInterval(build_table_from_json, 60000);
$(document).ready(do_table_sort);
