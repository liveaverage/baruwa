function handle_listing(event){
    event.preventDefault();
    $(this).blur();
    var list_confirm = [];
    var count = 0;
    var stored_email = $(this).attr('title');
    var addr_array = $('#toaddr').attr('title').split(',');
    var list_name = $(this).attr('id');
    var to_addr = addr_array[0];
    if ($(this).attr('id') == 'whitelist') {
        var list_type = 1; 
    }else{
        var list_type = 2;
    };
    list_confirm[count++] = '<div id="confirm-listing">';
    list_confirm[count++] = '<div id="confirm-listing-info">';
    list_confirm[count++] = 'This will '+$(this).attr('id')+' mail from ';
    list_confirm[count++] = '<span id="listby">'+ $(this).attr('title') +'</span>';
    list_confirm[count++] = ' to '+to_addr;
    list_confirm[count++] = '</div>';
    list_confirm[count++] = '<div id="confirm-listing-buttons">';
    list_confirm[count++] = gettext('List by IP address')+' <input type="checkbox" id="byip" />';
    list_confirm[count++] = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; '+gettext('Do you want to continue ?')+' ';
    list_confirm[count++] = '<input type="button" id="yes_list" value="'+gettext('Yes')+'"/>';
    list_confirm[count++] = '<input type="button" id="no" value="'+gettext('No')+'"/>';
    list_confirm[count++] = '</div>';
    list_confirm[count++] = '</div>';
    if ($('#confirm-listing').length) {
        $('#confirm-listing').remove();
    };
    if ($('#filter-error').length) {
        clearTimeout(timeout);
        $('#filter-error').empty().remove();
    };
    $('#fromaddr').after(list_confirm.join("\n"));
    $('#byip').bind('click', function(event) {
        //event.preventDefault();
        if ($('#byip').is(":checked")) {
            $('#listby').empty().append($('#clientip').text());
        }else{
            $('#listby').empty().append(stored_email);
        };   
    });
    $('#no').bind('click', function(event) {
        event.preventDefault();
        $('#confirm-listing').remove();
    });
    $('#yes_list').bind('click', function(event) {
        event.preventDefault();
        $('#yes_list').attr({'disabled':'disabled','value':gettext('Submitting')});
        if ($('#listing').attr('title') == '1' ||  $('#listing').attr('title') == '2') {
            var addr_parts = to_addr.split('@');
            var list_params = {
                user_part: addr_parts[0],
                to_address: addr_parts[1],
                from_address: $('#listby').text(),
                list_type: list_type
            };
        }else{
            var list_params = {
                to_address: to_addr,
                from_address: $('#listby').text(),
                list_type: list_type
            };
        };
        ajax_target = 2;
        $.post('/lists/add/', list_params, function(response, textStatus, xhr) {
            if (response.success) {
                $('.Grid_content').before('<div id="in-progress">'+$('#listby').text()+gettext(' has been added to your ')+list_name+'.</div>');
                $('#in-progress').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>');
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(ip);$('#in-progress').empty().remove();});
                $('#confirm-listing').remove();
                ip = setTimeout(function() {$('#in-progress').empty().remove();}, 15050);
                window.scroll(0,0);
            }else{
                $('#confirm-listing').remove();
                $('#fromaddr').after('<div id="filter-error">'+gettext('Error adding to ')+list_name+': '+response.error_msg+'</div>');
                $('#filter-error').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>');
                timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});  
            };
            $('#yes_list').removeAttr('disabled').attr({'value':gettext('Yes')});
        }, "json");   
    });
}

function handle_ajax(){
    $('#my-spinner')
    .ajaxStart(function(){$(this).empty().append('&nbsp;'+gettext('Processing...')).show();})
    .ajaxStop(function(){if(!$('.ajax_error').length){$(this).hide();}})
    .ajaxError(function(event, request, settings){
        $(this).hide();
        if(request.status == 200){
            if (ajax_target == 1) {
                if($('#filter-ajax').length){$('#filter-ajax').remove();}
                $("#submit_q_request").removeAttr('disabled');
                $('#qheading').after('<div id="filter-error">'+gettext('Empty server response')+'</div>');
            }else{
                $('#confirm-listing').remove();
                $('#fromaddr').after('<div id="filter-error">'+gettext('Empty server response')+'</div>');
            };
            $('#filter-error').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>');
            timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
            $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});
        }else{
            if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
            if (ajax_target == 1) {
                if($('#filter-ajax').length){$('#filter-ajax').remove();}
                $("#submit_q_request").removeAttr('disabled');
                $('#qheading').after('<div id="filter-error">'+gettext('Error connecting to server. check network!')+'</div>');
            }else{
                $('#confirm-listing').remove();
                $('#fromaddr').after('<div id="filter-error">'+gettext('Error connecting to server. check network!')+'</div>');
            };
            $('#filter-error').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>');
            timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
            $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});
        }
    });
}
function do_quarantine_release(event){
    $("#submit_q_request").attr('disabled', 'disabled');
    if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
    if($('#info-msg').length){clearTimeout(timeout);$('#info-msg').remove();}
    $('#qheading').after('<div id="filter-ajax">'+gettext('Processing request.............')+'</div>');
    var release  = 0;
    var todelete = 0;
    var salearn  = 0;
    var use_alt  = 0;

    event.preventDefault();

    if($("#id_release").is(":checked")){
        release = 1;
    }
    if($("#id_todelete").is(":checked")){
        todelete = 1;
    }
    if($("#id_salearn").is(":checked")){
        salearn = 1;
    }
    if($("#id_use_alt").is(":checked")){
         use_alt = 1;
    }
    var quarantine_process_request = {
        release:        release, 
        todelete:       todelete,
        salearn:        salearn,
        salearn_as:     $("#id_salearn_as").val(),
        use_alt:        use_alt,
        altrecipients:  $("#id_altrecipients").val(),
        message_id:     $("#id_message_id").val() 
    };
    ajax_target = 1;
    //fix for IE, it does not handle #q properly
    var url = $('#qform').attr('action');
    var hash = url.indexOf("#");
    url = url.slice(0, hash);
    $.post(url,quarantine_process_request,
        function(response){
            $('#filter-ajax').remove();
            if(response.success){
                if($('#info-msg').length){clearTimeout(timeout);$('#info-msg').remove();}
                $('#qheading').after('<div id="info-msg">'+response.html+'</div>');
                $('#info-msg').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>')
                timeout = setTimeout(function() {$('#info-msg').remove();}, 15050);
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#info-msg').empty().remove();});
            }else{
                if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
                $('#qheading').after('<div id="filter-error">'+response.html+'</div>');
                $('#filter-error').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>')
                timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});
            }
            $("#submit_q_request").removeAttr('disabled');
        },"json");
}

var ajax_target = 1;
$(document).ready(function() {
    handle_ajax();
    mh = $('#mail-headers');
    mh.hide();
    mh.after($("<a/>").attr({href:'#',id:'header-toggle',innerHTML:'<img src="/static/imgs/maximize.png" alt="&darr;">&nbsp;'+gettext('Show headers')}));
    $("#header-toggle").bind('click',function(event){
        event.preventDefault();
        if($("#mail-headers").css("display") == 'block'){
            $("#mail-headers").css({display:'none'})
            $(this).blur().html('<img src="/static/imgs/maximize.png" alt="&darr;">&nbsp;'+gettext('Show headers'));
            window.scroll(0,50);
        }else{
            $("#mail-headers").css({display:'block'})
            $(this).blur().html('<img src="/static/imgs/minimize.png" alt="&uarr;">&nbsp;'+gettext('Hide headers'));
        }
    });
    $("#qform").submit(do_quarantine_release);
    $('#listing a').bind('click', handle_listing);
});
