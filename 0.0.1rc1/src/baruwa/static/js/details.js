function do_spinner(){
    $('#my-spinner')
    .ajaxStart(function(){$(this).empty().append($("<img/>").attr("src","/static/imgs/loader-orig.gif")).append('&nbsp;Processing...');})
    .ajaxStop(function(){if(!$('.ajax_error').length){$(this).empty();}})
    .ajaxError(function(event, request, settings){
        if(request.status == 200){
            if(settings.url == '/messages/process_quarantine/'){
                location.href='/messages/';
            }else{
                location.href=settings.url;
            }
        }else{
            $(this).empty().append('<span class="ajax_error">Error connecting to server. check network!</span>');
            if($('#filter-ajax').length){$('#filter-ajax').remove();}
            $("#submit_q_request").removeAttr('disabled');
            if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
            $('#qheading').after('<div id="filter-error">Error connecting to server. check network!</div>');
            $('#filter-error').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
            $('#dismiss a').click(function(event){event.preventDefault();$('#filter-error').empty().remove();});
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
        if($('#in-progress').length){clearTimeout(ip);$('#in-progress').empty().remove();}
        if(data.success == 'True'){
            $('.Grid_content').before('<div id="in-progress">'+data.html+'</div>');
            $('#in-progress').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
            ip = setTimeout(function() {$('#in-progress').empty().remove();}, 15050);
            window.scroll(0,0);
        }else{
            $('.Grid_content').before('<div id="in-progress">'+data.html+'</div>');
            $('#in-progress').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
            ip = setTimeout(function() {$('#in-progress').empty().remove();}, 15050);
            $("#"+id).after($('<a/>').attr({href:url,id:id}).html(id)).remove();
            $("#"+id).bind('click',confirm_listing);
            window.scroll(0,0);
        }
        $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(ip);$('#in-progress').empty().remove();});
    });
}

function formSubmission(event){
    $("#submit_q_request").attr('disabled', 'disabled');
    if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
    $('#qheading').after('<div id="filter-ajax">Processing request.............</div>');
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
            $('#filter-ajax').remove();
            if(response.success == 'True'){
                if($('#info-msg').length){clearTimeout(timeout);$('#info-msg').remove();}
                $('#qheading').after('<div id="info-msg">'+response.html+'</div>');
                $('#info-msg').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
                timeout = setTimeout(function() {$('#info-msg').remove();}, 15050);
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#info-msg').empty().remove();});
            }else{
                if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
                $('#qheading').after('<div id="filter-error">'+response.html+'</div>');
                $('#filter-error').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
                timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});
            }
            $("#submit_q_request").removeAttr('disabled');
        },"json");
}

function prepareDoc(){
    do_spinner();
    mh = $("#mail-headers");
    mh.hide();
    mh.after($("<a/>").attr({href:'#',id:'header-toggle',innerHTML:'<img src="/static/imgs/maximize.png" alt="&darr;">&nbsp;Show headers'}));
    $("#header-toggle").bind('click',function(event){
        event.preventDefault();
        if($("#mail-headers").css("display") == 'block'){
            $("#mail-headers").css({display:'none'})
            $(this).blur().html('<img src="/static/imgs/maximize.png" alt="&darr;">&nbsp;Show headers');
            window.scroll(0,50);
        }else{
            $("#mail-headers").css({display:'block'})
            $(this).blur().html('<img src="/static/imgs/minimize.png" alt="&uarr;">&nbsp;Hide headers');
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
