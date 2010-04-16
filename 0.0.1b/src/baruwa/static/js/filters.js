function handlePost(event){
    $('#submit-button').attr('disabled','disabled');
    $('#cancel-button').attr('disabled','disabled');
    event.preventDefault();
    var filter_add_request = {
        username: $('#id_username').val(),
        filter: $('#id_filter').val(),
        active: $('#id_active').val()
    };
    $.post($("#filter_form").attr("action"),filter_add_request,
        function(response){
            if(response.success == 'True'){
                url = '/accounts/user/delete/filter/'+response.data[2]+'/'+response.data[0]+'/';
                id = response.data[0].toLowerCase().replace(/\s+/g,'-').replace(/[^a-z0-9\-]/g,'');
                $('tbody').append('<tr id="'+id+'"><td class="first-t">'+response.data[0]+'</td><td class="first-t">'+response.data[1]+'</td><td class="first-t"><a href="'+url+'">Delete</a></td></tr>');
                window.scroll(0,0);
                $("#in-progress").html(response.html).fadeIn(50).delay(15000).slideToggle('fast');
                $('tbody a').bind('click',confirm_delete);
            }else{
                window.scroll(0,0);
                $("#in-progress").html(response.html).fadeIn(50).delay(15000).slideToggle('fast');
            }
    },"json");
    $('#submit-button').removeAttr('disabled');
    $('#cancel-button').removeAttr('disabled');
}

var $dialog = $('<div></div>');
$(document).ready(function(){
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
    $('#filter_form').submit(handlePost);
});
