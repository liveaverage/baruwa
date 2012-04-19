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
function ajax_start(){
    if ($('#in-progress').length) {
        $('#in-progress').remove();
    }
    $('#Footer_container').after(loading_msg);
}

function ajax_stop(){
    $('#loading_message').remove();
}

function ajax_error(event, request, settings){
    if(request.status == 200){
        location.href=settings.url;
    }else{
        $('.Grid_heading').before('<div id="ajax-error-msg" class="ui-state-highlight">'+gettext('Server error')+'</div>');
        setTimeout(function() {
            $('#ajax-error-msg').empty().remove();
        }, 3900);
    }
    $('#loading_message').remove();
}

function check_status(url){
    $.get(url, function(response){
        if (response.completed) {
            if($('#in-progress').length){$('#in-progress').remove();}
            $('.Grid_content').before('<div id="in-progress">'+response.html+'</div>');
            $('#in-progress').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>');
            var ip = setTimeout(function() {$('#in-progress').remove();}, 15050);
            $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(ip);$('#in-progress').empty().remove();});
            $('a.selector').bind('click', test_conn);
            clearInterval(auto_refresh);
        }
    }, "json");
}

function test_conn(event){
    event.preventDefault();
    if ($('#in-progress').length) {
        return;
    }
    var url = $(this).attr('href');
    auto_refresh = setInterval(check_status(url), 5000);
}

var auto_refresh, loading_msg;
loading_msg = '<div id="loading_message"><div id="loading">';
loading_msg += '<img src="'+media_url+'imgs/ajax-loader.gif" alt="loading"/>';
loading_msg += '<br/><b>'+gettext('Testing connection')+'</b></div></div>';
$(document).ready(function(){
    $('body').ajaxStart(ajax_start).ajaxStop(ajax_stop).ajaxError(ajax_error);
    $('a.selector').bind('click', test_conn);
});