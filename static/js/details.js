function handleListing(event){
    event.preventDefault();
    url = $(this).attr('href');
    id = $(this).attr('id');
    $("#"+id).before($("<img/>").attr({src:"/static/imgs/loader.gif",id:"img-loading"})).remove();
    $.getJSON(url,function(data){
        if(data.success == 'True'){
            $("#in-progress").html(data.html).fadeIn(50).delay(15000).slideToggle('fast');
            $("#img-loading").after(id).remove();
            window.scroll(0,0);
        }else{
            $("#in-progress").html(data.html).fadeIn(50).delay(15000).slideToggle('fast');
            $("#img-loading").after($('<a/>').attr({href:url,id:id}).html(id)).remove();
            window.scroll(0,0);
        }
    });
}

function formSubmission(event){
    $("#submit_q_request").attr('disabled', 'disabled');
    $("#quarantine_errors").empty();
    $("#ajax_status").html($("<img/>").attr("src","/static/imgs/loader.gif")).append('&nbsp;Refreshing........'); 
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
            }
        },"json");
}

function prepareDoc(){
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
        $("#whitelist").bind('click',handleListing);
    }
    if($("#blacklist").length){
        $("#blacklist").bind('click',handleListing);
    }

}

$(document).ready(prepareDoc);
