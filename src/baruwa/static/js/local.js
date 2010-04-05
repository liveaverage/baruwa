
function processQuarantine(){
    $("#submit_q_request").attr('disabled', 'disabled');
    $("#quarantine_errors").empty();
   var release  = 0;
   var todelete = 0;
   var salearn  = 0;
   var use_alt  = 0;

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
        message_id:     $("#id_message_id").val() };
    $.post("/messages/process_quarantine/", quarantine_process_request,
        function(response){
            $("#quarantine_errors").empty();
            $("#server_response").empty();
            if(response.success == "True"){
                $("#server_response").prepend(response.html).slideDown();
                $("#process_quarantine").slideToggle();
            }else{
                $("#quarantine_errors").append(response.html);
                $("#submit_q_request").removeAttr('disabled');
            }
        }, "json");
    return false;
}

function prepareDoc(){
    $("#qform").submit(processQuarantine);
    $("#ajax_status").ajaxSend(function() {
      $(this).append('<img src="/static/imgs/loader.gif" />&nbsp;Processing the request...');
    });
    $("#ajax_status").ajaxStop(function() {
      $(this).empty();
      $(this).slideToggle();
    });
}

$(document).ready(prepareDoc);
