function do_spinner(){
    $('#my-spinner')
    .ajaxStart(function(){$(this).empty().append($("<img/>").attr("src","/static/imgs/loader-orig.gif")).append('&nbsp;Processing...');})
    .ajaxStop(function(){$(this).empty();})
    .ajaxError(function(event, request, settings){
        if(request.status == 200){
            if(settings.url == '/messages/process_quarantine/'){
                location.href='/messages/';
            }else{
                location.href=settings.url;
            }
        }else{
            $(this).empty();
        }
    });
}
function confirm_listing(event){
    re = /\/messages\/(whitelist|blacklist)\/.+\//
    str = $(this).attr('href');
    aobj = $(this);
    found = str.match(re);
    if(found.length == 2){
        event.preventDefault();
        clearTimeout(ip);
        alt = 'This will '+found[1]+' all emails with "From address" '+$('#from-addr').text()+'<br/><b>Do you wish to continue ?</b>';
        $dialog.html(alt);
        $dialog.dialog('option','buttons',{
            'Yes':function(){
                $(this).dialog('close');
                handleListing(event,aobj);
            },'No':function(){
                $(this).dialog('close');
            }
        });
        $dialog.dialog('open');
    }
}

function handleListing(event,aobj){
    url = aobj.attr('href');
    id = aobj.attr('id');
    $("#"+id).before($("<span/>").attr({id:id,innerHTML:id})).remove();
    $.getJSON(url,function(data){
        if(data.success == 'True'){
            $("#in-progress").html(data.html).append('<div id="dismiss"><a href="#">Dismiss</a></div>').fadeIn(0);
            ip = setTimeout(function(){$('#in-progress').hide('fast');},15000);
            window.scroll(0,0);
        }else{
            $("#in-progress").html(data.html).append('<div id="dismiss"><a href="#">Dismiss</a></div>').fadeIn(0);
            ip = setTimeout(function(){$('#in-progress').hide('fast');},15000);
            $("#"+id).after($('<a/>').attr({href:url,id:id}).html(id)).remove();
            $("#"+id).bind('click',confirm_listing);
            window.scroll(0,0);
        }
        $('#dismiss a').click(function(){clearTimeout(ip);$('#in-progress').hide();});
    });
}

function formSubmission(event){
    $("#submit_q_request").attr('disabled', 'disabled');
    $("#quarantine_errors").empty();
    $("#ajax_status").html($("<img/>").attr("src","/static/imgs/loader.gif")).append('&nbsp;Processing........'); 
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
    $.post('/messages/process_quarantine/',quarantine_process_request,
        function(response){
            $("#ajax_status").empty();
            $("#quarantine_errors").empty();
            $("#server_response").empty();
            if(response.success == 'True'){
                $("#server_response").prepend(response.html).slideDown();
                $("#process_quarantine").slideToggle();
            }else{
                $("#quarantine_errors").append(response.html);
                $("#submit_q_request").removeAttr('disabled');
                setTimeout(function(){$("#quarantine_errors").empty();},15000);
            }
        },"json");
}

function prepareDoc(){
    do_spinner();
    mh = $("#mail-headers");
    mh.hide();
    mh.after($("<a/>").attr({href:'#',id:'header-toggle',innerHTML:'&darr;&nbsp;Show headers'}));
    $("#header-toggle").bind('click',function(event){
        event.preventDefault();
        if($("#mail-headers").css("display") == 'block'){
            $("#mail-headers").css({display:'none'})
            $(this).blur().html("&darr;&nbsp;Show headers");
            window.scroll(0,50);
        }else{
            $("#mail-headers").css({display:'block'})
            $(this).blur().html("&uarr;&nbsp;Hide headers");
        }
    });
    $("#qform").submit(formSubmission);
    if($("#whitelist").length){
        $('#whitelist').bind('click',confirm_listing);
    }
    if($("#blacklist").length){
        $('#blacklist').bind('click',confirm_listing);
    }
    $dialog.html('An error occured !')
        .dialog({
            autoOpen: false,
            resizable: false,
            height:135,
            width: 500,
            modal: true,
            title: 'Please confirm listing ?',
            closeOnEscape: false,
            open: function(event, ui) {$(".ui-dialog-titlebar-close").hide();},
            draggable: false,
        });
}

var ip;
var $dialog = $('<div></div>');
$(document).ready(prepareDoc);
