
var $dialog = $('<div></div>');
$(document).ready(function(){
    if($("#add-item").is(':visible')){
        $('#add-item').hide();
        $('#add-sep').hide();
    }
    $('#user-update').bind('click',function(event){
        event.preventDefault();
        if($("#add-item").is(':visible')){
            $('#add-item').hide();
            $('#add-sep').hide();
            $('span.errors').empty();
            $("form")[0].reset();
            $(this).html('Update account').blur();
        }else{
            $('#add-item').show();
            $('#add-sep').show();
            $(this).html('Cancel account update').blur();
        }
    });
    $('#cancel-button').bind('click',function(){
        if($("#add-item").is(':visible')){
            $('#add-item').hide();
            $('#add-sep').hide();
            $('#user-update').html('Update account').blur();
            $("form")[0].reset();
            $('span.errors').empty();
        }
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
    $('tbody a').bind('click',confirm_delete);
});
