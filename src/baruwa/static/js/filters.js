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
                url = '/accounts/user/delete/filter/'+response.data[2]+'/'+response.data[3]+'/';
                id = response.data[3];
                $('#placeholder').remove();
                if(response.data[1] == 'Y'){
                    img = '<img title="Enabled" alt="Y" src="/static/imgs/action_check.png" />';
                }else{
                    img = '<img title="Disabled" alt="N" src="/static/imgs/action_check.png" />';
                }
                div = [];
                count = 0;
                div[count++] = '<div id="fid_'+id+'" class="whitelisted_div">';
                div[count++] = '<div class="Filters_row_name">'+response.data[0]+'</div>';
                div[count++] = '<div class="Filters_row_status">'+img+'</div>';
                div[count++] = '<div class="Filters_row_actions"><a href="'+url+'">';
                div[count++] = '<img title="Delete" alt="Delete" src="/static/imgs/action_delete.png" /></a></div>';
                div[count++] = '</div>';
                $("div.Grid_heading").after(div.join(''));
                window.scroll(0,0);
                if($('#in-progress').length){clearTimeout(ip);$('#in-progress').empty().remove();}
                $('.Grid_content').before('<div id="in-progress">'+response.html+'</div>');
                $('#in-progress').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
                ip = setTimeout(function() {clearTimeout(ip);$('#in-progress').remove();}, 15050);
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(ip);$('#in-progress').empty().remove();});
                $('div.Grid_heading ~ div a').bind('click',confirm_delete);
                $('.spanrow').remove();
                $('#add-item').dialog('close');
            }else{
                window.scroll(0,0);
                $('#id_'+response.form_field).addClass('ui-state-error');
                if($('#ajax-error-msg').length){clearTimeout(timeout);$('#ajax-error-msg').empty().remove();}
                $('#filter_form').before('<div id="ajax-error-msg" class="ui-state-highlight">'+response.html+'</div>');
                timeout = setTimeout(function() {
                    $('#ajax-error-msg').empty().remove();
                }, 3900);
            }
            $('#submit-button').removeAttr('disabled');
            $('#cancel-button').removeAttr('disabled');
    },"json");
}

var $dialog = $('<div></div>');
$(document).ready(function(){
    $("#add-item").dialog({
        autoOpen: false,
        height: 200,
        width: 280,
        modal: true,
        title: 'Add filter',
        closeOnEscape: false,
        open: function(event, ui) {$(".ui-dialog-titlebar-close").hide();},
    });

    $('#add-item').dialog('open');

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
    $('#filter_form').submit(handlePost);
    $('#cancel-button').bind('click',function(){
        $('form').clearForm();
        $('#add-item').dialog('close');
        $('input').removeClass('ui-state-error');
        $('#filter-add').bind('click',function(event){event.preventDefault();$('#add-item').dialog('open');});
    });
    $('#filter-add').bind('click',function(event){event.preventDefault();$('#add-item').dialog('open');});
});
