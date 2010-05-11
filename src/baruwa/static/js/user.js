function handlePost(event){
    $('#submit-button').attr('disabled','disabled');
    $('#cancel-button').attr('disabled','disabled');
    $('input').removeClass('ui-state-error');
    event.preventDefault();
    if ($('#id_type').length){
        type = $('#id_type').val();
    }else{
        type = '';
    }
    var accounts_create_request = {
        username: $('#id_username').val(),
        fullname: $('#id_fullname').val(),
        password: $('#id_password').val(),
        type: type,
        quarantine_report: $('#id_quarantine_report').val(),
        quarantine_rcpt: $('#id_quarantine_rcpt').val(),
        noscan: $('#id_noscan').val(),
        spamscore: $('#id_spamscore').val(),
        highspamscore: $('#id_highspamscore').val()
    };
    $.post($('#update-account-form').attr('action'),accounts_create_request,
        function(response){
            if(!response.error){
                if($('#in-progress').length){clearTimeout(ip);$('#in-progress').empty().remove();}
                $('#add-item').dialog('close');
                $('.Grid_content').before('<div id="in-progress">The account has been updated</div>');
                $('#in-progress').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
                ip = setTimeout(function() {$('#in-progress').remove();}, 15050);
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(ip);$('#in-progress').empty().remove();});
            }else{
                $('#id_'+response.form_field).addClass('ui-state-error');
                $('#update-account-form').before('<div id="ajax-error-msg" class="ui-state-highlight form_row">'+response.error+'</div>');
                setTimeout(function() {
                    $('#ajax-error-msg').empty().remove();
                }, 3900);
            }
            $('#submit-button').removeAttr('disabled');
            $('#cancel-button').removeAttr('disabled');
        },'json');
}

var $dialog = $('<div></div>');
$(document).ready(function(){
    $("#add-item").dialog({
        autoOpen: false,
        height: 460,
        width: 380,
        modal: true,
        title: 'Update account',
        closeOnEscape: false,
        open: function(event, ui) {$(".ui-dialog-titlebar-close").hide();},
    });

    $('#user-update').bind('click',function(event){
        event.preventDefault();
        $('#add-item').dialog('open');
        $('input').removeClass('ui-state-error');
        $(this).blur();
    });

    $('#cancel-button').bind('click',function(){
        $('input').removeClass('ui-state-error');
        $('.form_error').empty();
        $('#add-item').dialog('close');
    });

    $dialog.html('An error occured !')
        .dialog({
            autoOpen: false,
            resizable: false,
            height:120,
            width: 350,
            modal: true,
            title: 'Please confirm deletion ?',
            closeOnEscape: false,
            open: function(event, ui) {$(".ui-dialog-titlebar-close").hide();},
            draggable: false,
        });
    $('div.Grid_heading ~ div a').bind('click',confirm_delete);
    $('#update-account-form').submit(handlePost);
});
