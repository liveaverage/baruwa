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
function prevent_interupt_refresh(event){
    if(ax_in_progress){
        event.preventDefault();
        if(!$("#in-progress").length){
            $('.Grid_content').before('<div id="in-progress">'+gettext('Content refresh in progress, please wait for it to complete')+'</div>');
            setTimeout(function() {$('#in-progress').remove();}, 15050);
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
            clearTimeout(auto_refresh);
        }
        $("a").bind('click',prevent_interupt_refresh);
        setTimeout(build_table_from_json,60000);
    }
}

function do_table_sort(){
    full_messages_listing = false;
    $('.nojs').remove();
    ax_in_progress = false;
	$("#heading small").empty().append(gettext("[updated every 60 sec's]"));
    $("#my-spinner").ajaxSend(function(){
	    $(this).empty().append('&nbsp;'+gettext('Refreshing...')).show();
	    ax_error = false;
        ax_in_progress = true;
    })
    .ajaxStop(function() {
	    if(!ax_error){
		    var lu = lastupdatetime();
		    $("#heading small").empty().append(gettext('[last update at ')+lu+']');
            $('#my-spinner').hide();
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
	        $(this).empty().append('<span class="ajax_error">'+gettext('Error connecting to server. check network!')+'</span>').show();
	        ax_error = true;
            ax_in_progress = false;
            if($("#in-progress").is(':visible')){
                $("#in-progress").hide();
            }
            auto_refresh = setTimeout(build_table_from_json,60000);
        }
    });
    $('a').bind('click',prevent_interupt_refresh);
}

var auto_refresh = setInterval(build_table_from_json, 60000);
$(document).ready(do_table_sort);
