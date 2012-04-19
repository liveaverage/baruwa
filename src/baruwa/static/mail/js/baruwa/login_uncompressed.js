$(document).ready(function(){
    $('#resetlnk').bind('click', function(event){
        event.preventDefault();
        $('#login_part').hide();
        $('#forgottenpw').show();
    });
    $('#cancelrset').bind('click', function(event){
        event.preventDefault();
        $('#forgottenpw').hide();
        $('#login_part').show();
    });
  $('#lang').change(function(){
      var lang = $('#lang').val();
      var post_data = {
         language: lang,
         next: next + $('#loginform [name=next]').val(),
         csrfmiddlewaretoken: $('#loginform [name=csrfmiddlewaretoken]').val()
      }
      $.post(url, post_data, function(response){
      location.href = next + $('#loginform [name=next]').val();
      });
  });
  $('html').ajaxSend(function(){
     $('#login').attr('disabled', 'disabled');
  }).ajaxStop(function(){
     $('#login').removeAttr('disabled');
  });
});