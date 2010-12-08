// 
// Baruwa - Web 2.0 MailScanner front-end.
// Copyright (C) 2010  Andrew Colin Kissa <andrew@topdog.za.net>
// 
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//
// vim: ai ts=4 sts=4 et sw=4
//
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
        $("#afilters").empty().append('<div class="LightBlue_div"><div class="spanrow">'+gettext('No active filters at the moment')+'</div></div>');
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
        $("#sfilters").empty().append('<div class="LightBlue_div"><div class="spanrow">'+gettext('No saved filters at the moment')+'</div></div>');
    }
    $("#sfilters div a").bind('click',ajaxify_active_filter_links);
}

function build_page(response){
    if(response.success){
        update_counters(response.data);
        build_active_filters(response.active_filters);
        build_saved_filters(response.saved_filters);
    }else{
        if($('#filter-error').length){clearTimeout(timeout);$('#filter-error').remove();}
        $('#aheading').after('<div id="filter-error">'+response.errors+'</div>');
        $('#filter-error').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>')
        timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
        $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});
    }
    $("#filter_form_submit").removeAttr('disabled').attr('value',gettext('Add'));;
}

function build_elements(response){
    if(response.success){
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
                    row = '<div class="LightBlue_div"><div class="spanrow">'+gettext('No saved filters at the moment')+'</div></div>';
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
        $('#filter-error').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>')
        timeout = setTimeout(function() {$('#filter-error').remove();}, 15050);
        $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(timeout);$('#filter-error').empty().remove();});
    }
    $("#filter_form_submit").removeAttr('disabled').attr('value',gettext('Add'));
    $("#filter-ajax").remove();
}

function ajaxify_active_filter_links(e){
    e.preventDefault();
    $("#filter_form_submit").attr({'disabled':'disabled','value':gettext('Loading')});
    $.get($(this).attr('href'),build_page,'json');
}

function addFilter(){
    $("#filter_form_submit").attr({'disabled':'disabled','value':gettext('Loading')});
    $('#afform').after('<div id="filter-ajax">'+gettext('Processing request.............')+'</div>');
    var add_filter_request = {
        filtered_field: $("#id_filtered_field").val(),
        filtered_by: $("#id_filtered_by").val(),
        filtered_value: $("#id_filtered_value").val()
    };
    $.post("/reports/",add_filter_request,build_elements,"json");
    return false;
}

$(document).ready(function(){
    bool_fields = ["scaned","spam","highspam","saspam","rblspam","whitelisted","blacklisted","virusinfected","nameinfected","otherinfected","isquarantined"];
    num_fields = ["size","sascore"];
    text_fields = ["id","from_address","from_domain","to_address","to_domain","subject","clientip","spamreport","headers", "hostname"];
    time_fields = ["date","time"];
    num_values = [{'value':1,'opt':gettext('is equal to')},{'value':2,'opt':gettext('is not equal to')},
                    {'value':3,'opt':gettext('is greater than')},{'value':4,'opt':gettext('is less than')}];
    text_values = [{'value':1,'opt':gettext('is equal to')},{'value':2,'opt':gettext('is not equal to')},
                    {'value':9,'opt':gettext('is null')},{'value':10,'opt':gettext('is not null')},
                    {'value':5,'opt':gettext('contains')},{'value':6,'opt':gettext('does not contain')},
                    {'value':7,'opt':gettext('matches regex')},{'value':8,'opt':gettext('does not match regex')}];
    time_values = [{'value':1,'opt':gettext('is equal to')},{'value':2,'opt':gettext('is not equal to')},
                    {'value':3,'opt':gettext('is greater than')},{'value':4,'opt':gettext('is less than')}];
    bool_values = [{'value':11,'opt':'is true'},{'value':12,'opt':'is false'}];
    $('#id_filtered_field').prepend('<option value="0" selected="0">'+gettext('Please select')+'</option>');
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
    $("#my-spinner").ajaxStart(function(){$(this).empty().append('&nbsp;'+gettext('Processing...')).show();})
        .ajaxError(function(event, request, settings){
            if(request.status == 200){
                location.href=settings.url;
            }else{
                $(this).empty().append($("<span/>").addClass('ajax_error')).append('&nbsp;'+gettext('Error occured'));
            }
        }).ajaxStop(function(){$(this).empty().hide();});
    $("#afilters div a").bind('click',ajaxify_active_filter_links);
    $("#sfilters div a").bind('click',ajaxify_active_filter_links);
});
