function build_elements(response){
    if(response.success == "True"){
        if(response.active_filters){
            var i = response.active_filters.length;
            i--;
            if(i > 0){
                $("#afilters tbody tr:last").removeClass('last');
                n = response.active_filters[i];
                var row = '<tr class="last"><td class="first-t filters" colspan="2">[ <a href="/reports/fd/'+i+'/">x</a> ]';
                row += ' [ <a href="/reports/fs/'+i+'/">Save</a> ] '+n.filter_field+' '+n.filter_by+' '+n.filter_value+'</td></tr>';
                $("#afilters tbody").append(row);
            }else{
                window.location.href=window.location.href;
            }
        }
        if(response.saved_filters){
            $("#sfilters tbody").empty();
            var i = response.saved_filters.length;
            i--;
            $.each(response.saved_filters,function(itr,filter){
                if(itr == i){
                    var row = '<tr class="last">';
                }else{
                    var row = '<tr>';
                }
                row += '<td class="first-t filters" colspan="2">[ <a href="/reports/sfd/'+filter.filter_id+'/">x</a> ]';
                if(!filter.is_loaded){
                    row += ' [ <a href="/reports/sfl/'+filter.filter_id+'/">Load</a> ] ';
                }else{
                    row += ' [ Load ] ';
                }
                row += filter.filter_name+'</td></tr>';
                $("#sfilters tbody").append(row);
            });
        }
        $("#msgcount").html(response.data.count);
        $("#newestmsg").html(response.data.newest);
        $("#oldestmsg").html(response.data.oldest);
        $("#filter-form-errors").hide();
    }else{
        $("#filter-form-errors td").addClass('filter_errors');
        $("#filter-form-errors td").html(response.errors);
        $("#filter-form-errors").fadeIn(50).delay(30000).slideToggle('fast');
    }
    $("#filter_form_submit").removeAttr('disabled');
}

function addFilter(){
    $("#filter_form_submit").attr('disabled','disabled');
    var add_filter_request = {
        filtered_field: $("#id_filtered_field").val(),
        filtered_by: $("#id_filtered_by").val(),
        filtered_value: $("#id_filtered_value").val()
    };
    $.post("/reports/",add_filter_request,build_elements,"json");
    return false;
}

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
$("#filter-form").submit(addFilter);
$("#filter-form").ajaxSend(function(){
    $("#filter-form-errors td").empty();
    $("#filter-form-errors td").removeClass('filter_errors');
    $("#filter-form-errors td").html($("<img/>").attr("src","/static/imgs/loader-orig.gif")).append('&nbsp;Processing........')
    $("#filter-form-errors").show();
});
});
