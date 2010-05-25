
function update_counters(data){
    $("#msgcount").html(data.count);
    $("#newestmsg").html(data.newest);
    $("#oldestmsg").html(data.oldest);
}

function build_active_filters(active_filters){
    var i = active_filters.length;
    i--;
    rows = [];
    count = 0;
    $.each(active_filters,function(itr,filter){
        rows[count++] = '<div class="LightBlue_div">';
        rows[count++] = '<div class="Active_filters">';
        rows[count++] = '<div class="Filter_remove">';
        rows[count++] = '<a href="/reports/fd/'+itr+'/"><img src="/static/imgs/action_remove.png" alt="x" title="Remove" /></a>';
        rows[count++] = '</div>';
        rows[count++] = '<div class="Filter_save">';
        rows[count++] = '<a href="/reports/fs/'+itr+'/"><img src="/static/imgs/save.png" alt="Save" title="Save" /></a>';
        rows[count++] = '</div>';
        rows[count++] = '<div class="Filter_detail">';
        rows[count++] = filter.filter_field+' '+filter.filter_by+' '+filter.filter_value;
        rows[count++] = '</div>';
        rows[count++] = '</div>';
        rows[count++] = '</div>';
    });
    if(rows.length){
        $("#afilters").empty().append(rows.join(''));
    }else{
        $("#afilters").empty().append('<div class="LightBlue_div"><div class="spanrow">No active filters at the moment</div></div>');
    }
    $("#afilters div a").bind('click',ajaxify_active_filter_links);
}

function build_saved_filters(saved_filters){
    var i = saved_filters.length;
    i--;
    rows = [];
    count = 0;
    $.each(saved_filters,function(itr,filter){
        rows[count++] = '<div class="LightBlue_div">';
        rows[count++] = '<div class="Active_filters">';
        rows[count++] = '<div class="Filter_remove">';
        rows[count++] = '<a href="/reports/sfd/'+filter.filter_id+'/"><img src="/static/imgs/action_delete.png" alt="x" title="Delete" /></a>';
        rows[count++] = '</div>';
        rows[count++] = '<div class="Filter_save">';
        if(!filter.is_loaded){
            rows[count++] = '<a href="/reports/sfl/'+filter.filter_id+'/"><img src="/static/imgs/action_add.png" alt="Load" title="Load" /></a>';
        }else{
            rows[count++] = '<img src="/static/imgs/action_add.png" alt="Load" />';
        }
        rows[count++] = '</div>';
        rows[count++] = '<div class="Filter_detail">';
        rows[count++] = filter.filter_name;
        rows[count++] = '</div>';
        rows[count++] = '</div>';
        rows[count++] = '</div>';
    });
    if(rows.length){
        $("#sfilters").empty().append(rows.join(''));
    }else{
        $("#sfilters").empty().append('<div class="LightBlue_div"><div class="spanrow">No saved filters at the moment</div></div>');
    }
    $("#sfilters div a").bind('click',ajaxify_active_filter_links);
}

function build_page(response){
    if(response.success == 'True'){
        update_counters(response.data);
        build_active_filters(response.active_filters);
        build_saved_filters(response.saved_filters);
    }else{
        if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
        $('#aheading').after('<div id="filter-error">'+response.errors+'</div>');
        $('#filter-error').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
        timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
        $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});
    }
    $("#filter_form_submit").removeAttr('disabled').attr('value','Add');;
}

function build_elements(response){
    if(response.success == "True"){
        if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
        if(response.active_filters){
            var i = response.active_filters.length;
            i--;
            if(i > 0){
                n = response.active_filters[i];
                count = 0;
                row = [];
                row[count++] = '<div class="whitelisted_div">';
                row[count++] = '<div class="Active_filters">';
                row[count++] = '<div class="Filter_remove">';
                row[count++] = '<a href="/reports/fd/'+i+'/"><img src="/static/imgs/action_remove.png" alt="x" title="Remove" /></a>';
                row[count++] = '</div>';
                row[count++] = '<div class="Filter_save">';
                row[count++] = '<a href="/reports/fs/'+i+'/"><img src="/static/imgs/save.png" alt="Save" title="Save" /></a>';
                row[count++] = '</div>';
                row[count++] = '<div class="Filter_detail">';
                row[count++] = n.filter_field+' '+n.filter_by+' '+n.filter_value;
                row[count++] = '</div>';
                row[count++] = '</div>';
                row[count++] = '</div>';
                $("#afilters").append(row.join(''));
                setTimeout(function(){$('div.whitelisted_div').removeClass('whitelisted_div').addClass('LightBlue_div');},15000);
                $('form').clearForm();
            }else{
                n = response.active_filters[0];
                if(n){
                    count = 0;
                    row = [];
                    row[count++] = '<div class="whitelisted_div">';
                    row[count++] = '<div class="Active_filters">';
                    row[count++] = '<div class="Filter_remove">';
                    row[count++] = '<a href="/reports/fd/'+i+'/"><img src="/static/imgs/action_remove.png" alt="x" title="Remove" /></a>';
                    row[count++] = '</div>';
                    row[count++] = '<div class="Filter_save">';
                    row[count++] = '<a href="/reports/fs/'+i+'/"><img src="/static/imgs/save.png" alt="Save" title="Save" /></a>';
                    row[count++] = '</div>';
                    row[count++] = '<div class="Filter_detail">';
                    row[count++] = n.filter_field+' '+n.filter_by+' '+n.filter_value;
                    row[count++] = '</div>';
                    row[count++] = '</div>';
                    row[count++] = '</div>';
                    $("#afilters").empty().append(row.join(''));
                }else{
                    row = '<div class="LightBlue_div"><div class="spanrow">No saved filters at the moment</div></div>';
                    $("#afilters").empty().append(row);
                }
            }
            $("#afilters div a").bind('click',ajaxify_active_filter_links);
        }
        if(response.saved_filters){
            build_saved_filters(response.saved_filters);
        }
        update_counters(response.data);
    }else{
        if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
        $('#aheading').after('<div id="filter-error">'+response.errors+'</div>');
        $('#filter-error').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
        timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
        $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});
    }
    $("#filter_form_submit").removeAttr('disabled').attr('value','Add');
    $("#filter-ajax").remove();
}

function ajaxify_active_filter_links(e){
    e.preventDefault();
    $("#filter_form_submit").attr({'disabled':'disabled','value':'Loading'});
    $.get($(this).attr('href'),build_page,'json');
}

function addFilter(){
    $("#filter_form_submit").attr({'disabled':'disabled','value':'Loading'});
    $('#afform').after('<div id="filter-ajax">Processing request.............</div>');
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
        $('#id_filtered_value').attr({'disabled':'disabled'}).val("");
    }
    if($.inArray($(this).val(),num_fields) != -1){
        $('#id_filtered_by').empty();
        $.each(num_values,function(i,n){
            $('#id_filtered_by').append($("<option/>").attr({value:n.value,innerHTML:n.opt}));
        });
        $('#id_filtered_value').removeAttr("disabled").val("");
    }
    if($.inArray($(this).val(),text_fields) != -1){
        $('#id_filtered_by').empty();
        $.each(text_values,function(i,n){
            $('#id_filtered_by').append($("<option/>").attr({value:n.value,innerHTML:n.opt}));
        });
        $('#id_filtered_value').removeAttr("disabled").val("");
    }
    if($.inArray($(this).val(),time_fields) != -1){
        $('#id_filtered_by').empty();
        $.each(time_values,function(i,n){
            $('#id_filtered_by').append($("<option/>").attr({value:n.value,innerHTML:n.opt}));
        });
        $('#id_filtered_value').removeAttr("disabled").val("");
        if($(this).val() == 'date'){
            $('#id_filtered_value').val('YYYY-MM-DD');
        }
        if($(this).val() == 'time'){
            $('#id_filtered_value').val('HH:MM');
        }
    }
});
$("#filter-form").submit(addFilter);
$("#my-spinner").ajaxStart(function(){$(this).empty().append($("<img/>").attr('src','/static/imgs/loader-orig.gif')).append('&nbsp;Processing...');})
    .ajaxError(function(event, request, settings){
        if(request.status == 200){
            location.href=settings.url;
        }else{
            $(this).empty().append($("<span/>").addClass('ajax_error')).append('&nbsp;Error occured');
        }
    }).ajaxStop(function(){$(this).empty();});
$("#afilters div a").bind('click',ajaxify_active_filter_links);
$("#sfilters div a").bind('click',ajaxify_active_filter_links);

});
