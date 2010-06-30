function handle_form(event){
    event.preventDefault();
    if ($('#id_user_part').length) {    
        var list_post = {
            from_address: $('#id_from_address').val(),
            to_address: $('#id_to_address').val(),
            list_type: $('#id_list_type').val(),
            user_part: $('#id_user_part').val()
        };
    }else{
        var list_post = {
            from_address: $('#id_from_address').val(),
            to_address: $('#id_to_address').val(),
            list_type: $('#id_list_type').val()
        };
    };

    $.post($('#list-form').attr('post'), list_post, function(response) {
        if (response.success) {
            if ($('#info-msg').length) {
                clearTimeout(timeout);
                $('#info-msg').remove();
            };
            if ($('#filter-error').length) {
                clearTimeout(timeout);
                $('#filter-error').remove();
            };
            $('.Bayes_heading').after('<div id="info-msg">The address has been added to the list</div>');
            $('#info-msg').append('<div id="dismiss"><a href="#">Dismiss</a></div>');
            timeout = setTimeout(function() {$('#info-msg').empty().remove();}, 15050);
            $('form').clearForm();
            window.scroll(0,0);
             $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#info-msg').empty().remove();});
        }else{
            var error_field = '#id_'+response.form_field;
            $(error_field).addClass('input_error');
            if ($('#filter-error').length) {
                clearTimeout(timeout);
                $('#filter-error').remove();
            };
            if ($('#info-msg').length) {
                clearTimeout(timeout);
                $('#info-msg').remove();
            };
            $('.Bayes_heading').after('<div id="filter-error">'+response.error_msg+'</div>');
            $('#filter-error').append('<div id="dismiss"><a href="#">Dismiss</a></div>');
            timeout = setTimeout(function() {
                $('#filter-error').empty().remove(); 
                $(error_field).removeClass('input_error');
            }, 15050);
            window.scroll(0,0);
            $('#dismiss a').click(function(event){
                event.preventDefault();
                clearTimeout(timeout);
                $('#filter-error').empty().remove();
                $(error_field).removeClass('input_error');
            });
        };
    }, "json");
    
}
$(document).ready(function() {
    $('#list-form').submit(handle_form);
    $('#my-spinner').ajaxStart(function() {
        $(this).empty().append('Processing....').show();
    }).ajaxError(function(event, request, settings) {
        $(this).hide();
        $('.Bayes_heading').after('<div id="filter-error">Server Error occured</div>');
        $('#filter-error').append('<div id="dismiss"><a href="#">Dismiss</a></div>');
        timeout = setTimeout(function() {$('#filter-error').empty().remove();}, 15050);
        $('#dismiss a').click(function(event){event.preventDefault();
            clearTimeout(timeout);
            $('#filter-error').empty().remove();
        });
    }).ajaxStop(function() {
        $(this).hide();
    });    
});
