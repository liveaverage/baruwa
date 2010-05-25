function handlePost(event){
    $('#submit-button').attr('disabled','disabled');
    $('#cancel-button').attr('disabled','disabled');
    $('input').removeClass('ui-state-error');
    event.preventDefault();
    var accounts_create_request = {
        username: $('#id_username').val(),
        fullname: $('#id_fullname').val(),
        password: $('#id_password').val(),
        type: $('#id_type').val(),
        quarantine_report: $('#id_quarantine_report').val(),
        quarantine_rcpt: $('#id_quarantine_rcpt').val(),
        noscan: $('#id_noscan').val(),
        spamscore: $('#id_spamscore').val(),
        highspamscore: $('#id_highspamscore').val()
    };
    $.post('/accounts/',accounts_create_request,
        function(response){
            if(!response.error){
                location.href = '/accounts/';
            }else{
                $('#id_'+response.form_field).addClass('ui-state-error');
                $('#add-account-form').before('<div id="ajax-error-msg" class="ui-state-highlight form_row">'+response.error+'</div>');
                setTimeout(function() {
                    $('#ajax-error-msg').empty().remove();
                    $('#submit-button').removeAttr('disabled');
                    $('#cancel-button').removeAttr('disabled');
                }, 3900);
            }
        },'json');
}

$(document).ready(function(){
    $("#add-item").dialog({
        autoOpen: false,
        height: 460,
        width: 380,
        modal: true,
        title: 'Create an account',
        closeOnEscape: false,
        open: function(event, ui) {$(".ui-dialog-titlebar-close").hide();},
    });

    if($("#add-item").is(':visible')){
        $('#add-item').hide();
    }
    $('#user-add').bind('click',function(event){
        event.preventDefault();
        $('#add-item').dialog('open');
        $('input').removeClass('ui-state-error');
        $(this).blur();
        $('form').clearForm();
    });
    $('#cancel-button').bind('click',function(){
        $('form').clearForm();
        $('input').removeClass('ui-state-error');
        $('.form_error').empty();
        $('#add-item').dialog('close');
    });
    $('#add-account-form').submit(handlePost);
});
