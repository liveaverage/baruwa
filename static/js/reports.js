$(document).ready(function(){
bool_fields = ["archive","isspam","ishighspam","issaspam","isrblspam","spamwhitelisted","spamblacklisted","virusinfected","nameinfected","otherinfected","ismcp","ishighmcp","issamcp","mcpwhitelisted","mcpblacklisted","quarantined"];
num_fields = ["size","sascore","mcpscore"];
text_fields = ["id","from_address","from_domain","to_address","to_domain","subject","clientip","spamreport","mcpreport","headers"];
time_fields = ["date","time"];
num_values = [{'value':1,'opt':'is equal to'},{'value':2,'opt':'is not equal to'},{'value':3,'opt':'is greater than'},{'value':4,'opt':'is less than'}];
text_values = [{'value':1,'opt':'is equal to'},{'value':2,'opt':'is not equal to'},{'value':9,'opt':'is null'},{'value':10,'opt':'is not null'},{'value':5,'opt':'contains'},{'value':6,'opt':'does not contain'},{'value':7,'opt':'matches regex'},{'value':8,'opt':'does not match regex'}];
time_values = [{'value':1,'opt':'is equal to'},{'value':2,'opt':'is not equal to'},{'value':3,'opt':'is greater than'},{'value':4,'opt':'is less than'}];
bool_values = [{'value':11,'opt':'is true'},{'value':12,'opt':'is false'}];
$('#id_filtered_field').prepend('<option value="0" selected="0">Please select</option>');
$('#id_filtered_value').attr({'disabled':'disabled'});
$('#id_filtered_field').bind('change',function(){
    if($.inArray($(this).val(),bool_fields) != -1){
        $('#id_filtered_by').empty();
        $.each(bool_values,function(i,n){
            $('#id_filtered_by').append($("<option/>").attr({value:n.value,innerHTML:n.opt}));
        });
        $('#id_filtered_value').attr({'disabled':'disabled'});
    }
    if($.inArray($(this).val(),num_fields) != -1){
        $('#id_filtered_by').empty();
        $.each(num_values,function(i,n){
            $('#id_filtered_by').append($("<option/>").attr({value:n.value,innerHTML:n.opt}));
        });
        $('#id_filtered_value').removeAttr("disabled");
    }
    if($.inArray($(this).val(),text_fields) != -1){
        $('#id_filtered_by').empty();
        $.each(text_values,function(i,n){
            $('#id_filtered_by').append($("<option/>").attr({value:n.value,innerHTML:n.opt}));
        });
        $('#id_filtered_value').removeAttr("disabled");
    }
    if($.inArray($(this).val(),time_fields) != -1){
        $('#id_filtered_by').empty();
        $.each(time_values,function(i,n){
            $('#id_filtered_by').append($("<option/>").attr({value:n.value,innerHTML:n.opt}));
        });
        $('#id_filtered_value').removeAttr("disabled");
    }
});
});
