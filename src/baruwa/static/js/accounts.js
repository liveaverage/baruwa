$(document).ready(function(){
    if($("#add-item").is(':visible')){
        $('#add-item').hide();
        $('#add-sep').hide();
    }
    $('#user-add').bind('click',function(event){
        event.preventDefault();
        if($("#add-item").is(':visible')){
            $('#add-item').hide();
            $('#add-sep').hide();
            $('span.errors').empty();
            $("form")[0].reset();
            $(this).html('Create account').blur();
        }else{
            $('#add-item').show();
            $('#add-sep').show();
            $(this).html('Cancel account creation').blur();
        }
    });
    $('#cancel-button').bind('click',function(){
        if($("#add-item").is(':visible')){
            $('#add-item').hide();
            $('#add-sep').hide();
            $('#user-add').html('Create account').blur();
            $("form")[0].reset();
            $('span.errors').empty();
        }
    });
});
