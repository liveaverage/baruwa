function prevent_interupt_refresh(event){
    if(ax_in_progress){
        event.preventDefault();
        if(!$("#in-progress").is(':visible')){
            $("#in-progress").html("Content refresh in progress, please wait for it to complete").show('fast');
            window.scroll(0,0);
        }
    }
}

function build_table_from_json(){
    if(! ax_in_progress){
        if(last_ts != ''){
            $.ajaxSetup({'beforeSend':function(xhr){xhr.setRequestHeader("X-Last-Timestamp",last_ts);}});
        }
        $.getJSON('/messages/',json2html); 
        if(auto_refresh){
            clearInterval(auto_refresh);
        }
        $("#recent a").bind('click',prevent_interupt_refresh);
        setTimeout(build_table_from_json,60000);
    }
}

function do_table_sort(){
    full_messages_listing = false;
    $('.nojs').remove();
    ax_in_progress = false;
    $("#search-area").ajaxSend(function(){
	    $('#my-spinner').empty().append($("<img/>").attr("src","/static/imgs/loader-orig.gif")).append('&nbsp;Refreshing...');
	    ax_error = false;
        ax_in_progress = true;
    })
    .ajaxStop(function() {
	    if(!ax_error){
		    var lu = lastupdatetime();
		    $(this).empty().append('[last update at '+lu+']');
            $('#my-spinner').empty();
            ax_in_progress = false;
            if($("#in-progress").is(':visible')){
                $("#in-progress").hide();
            }
	    }
    })
    .ajaxError(function(event, request, settings){
        if(request.status == 200){
            location.href=settings.url;
        }else{
	        $(this).empty().append('<span class="ajax_error">Error connecting to server. check network!</span>');
            $('#my-spinner').empty();
	        ax_error = true;
            ax_in_progress = false;
            if($("#in-progress").is(':visible')){
                $("#in-progress").hide();
            }
            setTimeout(build_table_from_json,60000);
        }
    });
    $('a').bind('click',prevent_interupt_refresh);
}

var auto_refresh = setInterval(build_table_from_json, 60000);
$(document).ready(do_table_sort);
