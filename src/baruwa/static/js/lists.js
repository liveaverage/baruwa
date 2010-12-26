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
function ajax_start(){
    $(this).append('&nbsp;'+gettext('Processing...')).show();
    if ($('#in-progress').length) {
        $('#in-progress').remove();
    };
}

function ajax_stop(){
    $(this).empty().hide();
}

function ajax_error(event, request, settings){
    if(request.status == 200){
        if(settings.url == '/lists/add/'){
            location.href='/lists/';
        }else{
            location.href=settings.url;
        }
    }else{
        $(this).empty().append('<span class="ajax_error">'+gettext('Error connecting to server. check network!')+'</span>').show();
        $('.Grid_heading').before('<div id="ajax-error-msg" class="ui-state-highlight">'+gettext('Server error')+'</div>');
        setTimeout(function() {
            $('#ajax-error-msg').empty().remove();
        }, 3900);
    }
}

function toplinkize(list_kind,direction,field_name){
    var tmp = '';
    if(direction == 'dsc'){
        tmp = ' <a href="/lists/'+list_kind+'/asc/'+field_name+'/">&uarr;</a>';
    }else{
        tmp = ' <a href="/lists/'+list_kind+'/dsc/'+field_name+'/">&darr;</a>';
    }
    return tmp;
}

function paginate(){
    if(rj.list_kind == 1){
        lt = 'Whitelist :: ';
    }else{
        lt = 'Blacklist :: ';
    }
    fmt = gettext('Showing page %(page)s of %(pages)s pages.');
    data = {'page':rj.page, 'pages':rj.pages}
    tmp = interpolate(fmt, data, true);
    $('#heading').empty().append(lt+tmp);
    $.address.title('Baruwa :: '+gettext('List management ')+tmp);
    li = '';

    if(rj.show_first){
        tmp +='<span><a href="/lists/'+rj.list_kind+'/1/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/first_pager.png" alt="First"/></a></span>';
        tmp +='<span>.....</span>';
    }
    if(rj.has_previous){
        tmp +='<span><a href="/lists/'+rj.list_kind+'/'+rj.previous+'/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/previous_pager.png" alt="Previous"/></a></span>';
    }
    $.each(rj.page_numbers,function(itr,lnk){
        li = '/lists/'+rj.list_kind+'/'+lnk+'/'+rj.direction+'/'+rj.order_by+'/';
        if(rj.page == lnk){
            tmp +='<span><b>'+lnk+'</b>&nbsp;</span>';
        }else{
           tmp +='<span><a href="'+li+'">'+lnk+'</a>&nbsp;</span>'; 
        }
    });
    if(rj.has_next){
        tmp +='<span><a href="/lists/'+rj.list_kind+'/'+rj.next+'/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/next_pager.png" alt="Next"/></a></span>';
    }
    if(rj.show_last){
        tmp +='<span>......</span>';
        tmp +='<a href="/lists/'+rj.list_kind+'/last/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/last_pager.png" alt="Last"/></a></span>';
    }
    columns = "id to_address from_address";
    linfo = "hash To From"
    carray = columns.split(" ");
    larray = linfo.split(" ");
    for(i=0; i< carray.length;i++){
        if(larray[i] == 'hash'){h = '#';}else{h = larray[i];}
        if(rj.order_by == carray[i]){
            tmpl = toplinkize(rj.list_kind,rj.direction,carray[i]);
            $('.Lists_grid_'+larray[i]).empty().html(h).append(tmpl);
            $('#lists_filter_form').attr('action','/lists/'+rj.list_kind+'/'+rj.direction+'/'+carray[i]+'/');
        }else{
            ur = '<a href="/lists/'+rj.list_kind+'/'+rj.direction+'/'+carray[i]+'/">'+h+'</a>';
            $('.Lists_grid_'+larray[i]).empty().html(ur);
        }
    }
    $('#paginator').html(tmp);
    $('#paginator span a').bind('click',list_nav); 
    $('div.Grid_heading div a').bind('click',list_nav);
}

function lists_from_json(data){
    if(data){
        rj = data.paginator;
        tti = [];
        count = 0;
        css = 'LightGray';
        list_type = '1';
        $.each(data.items,function(i,n){
            list_type = rj.list_kind;
            if(n.from_address == 'any'){
                from_address = gettext('Any address');
            }else{
                from_address = n.from_address;
            }
            if(n.to_address == 'any'){
                to_address = gettext('Any address');
            }else{
                to_address = n.to_address;
            }
            link = '<a href="/lists/delete/'+n.id+'/"><img src="/static/imgs/action_delete.png" title="Delete" alt="Delete" /></a>';
            if(n.from_address == '127.0.0.1'){
                if(n.to_address == 'any'){
                    link = '=builtin=';
                }
            }

            if(css == 'LightBlue'){
                css = 'LightGray';
            }else{
                css = 'LightBlue';
            }

            tti[count++] = '<div id="list-id-'+n.id+'" class="'+css+'_div">';
            tti[count++] = '<div class="Lists_hash">'+n.id+'</div>';
            tti[count++] = '<div class="Lists_to">'+to_address+'</div>';
            tti[count++] = '<div class="Lists_from">'+from_address+'</div>';
            tti[count++] = '<div class="Lists_action">'+link+'</div>';
            tti[count++] = '</div>';
        });
        if(tti.length){
            $("div.Grid_heading").siblings('div').remove();
            $("div.Grid_heading").after(tti.join(''));
        }else{
            $("div.Grid_heading").siblings('div').remove();
            $("div.Grid_heading").after('<div class="LightBlue_div"><div class="spanrow">'+gettext('No items at the moment')+'</div></div>');
        }
        if(rj.order_by == 'id'){
            $('#filterbox').hide('fast');
        }else{
            $('#filterbox').show('fast');
            if(rj.order_by == 'to_address'){
                $('#filterlabel').html('<b>'+gettext('To:')+'</b>');
            }else{
                $('#filterlabel').html('<b>'+gettext('From:')+'</b>');
            }
        }
        $('div.Grid_heading ~ div a').bind('click',confirm_delete);
        paginate();
    }
}

function fetchPage(link,list_type){
    $.get(link,function(response){
        lists_from_json(response);
        if(list_type == '1'){
            lt = gettext('Blacklist');
            ll = '/lists/2/';
            ct = gettext('Whitelist :: ');
        }else{
            lt = gettext('Whitelist');
            ll = '/lists/1/';
            ct = gettext('Blacklist :: ');
        }
        $('#heading').empty().html(ct);
        $('#sub-menu-links ul li:first a').attr({id:'list-link',href:ll,innerHTML:lt});
    },'json');
}

function getPage(event){
    event.preventDefault();
    re = /\/lists\/([1-2])/
    link = $(this).attr('href');
    f = link.match(re);
    if(f){
        fetchPage(link,f[1]);
        url = link.replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
        $.address.value('?u='+url);
        $.address.history($.address.baseURL() + url);
    }
}

function submitForm(event){
    $('#id_lists_filter_submit').attr({'disabled':'disabled','value':gettext('Loading')});
    event.preventDefault();
    filter_request = {
        query_type: $("#id_query_type").val(),
        search_for: $("#id_search_for").val()
    };
    lk = $("#lists_filter_form").attr("action");
    $.post(lk,filter_request,
        function(response){
            lists_from_json(response);
            url = lk.replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
            $.address.value('?u='+url);
            $.address.history($.address.baseURL() + url);
        },"json");
    $('#id_lists_filter_submit').removeAttr('disabled').attr('value',gettext('Go'));
}

function confirm_delete(event) {
    event.preventDefault();
    $(this).blur();
    re = /\/lists\/delete\/([0-9]+)/
    l = $(this).attr('href');
    m = l.match(re)
    if (m) {
        del_warning = [];
        count = 0;
        del_warning[count++] = '<div id="confirm-del-msg">';
        del_warning[count++] = '<div id="confirm-del-info">';
        del_warning[count++] = gettext('This will delete the item ');
        del_warning[count++] = gettext('from the list. This action is not reversible');
        del_warning[count++] = '</div><div id="confirm-del-buttons">';
        del_warning[count++] = gettext('Do you wish to continue ?');
        del_warning[count++] = '&nbsp;<input type="button" value="Yes" id="yes_del" />&nbsp;';
        del_warning[count++] = '<input type="button" value="No" id="no_del" />'
        del_warning[count++] = '</div>';
        del_warning[count++] = '</div>'
        if ($('#confirm-del-msg').length) {
            $('#confirm-del-msg').remove();
        };
        $('#list-id-'+m[1]).after(del_warning.join(''));
        $('#no_del').bind('click', function(event) {
            event.preventDefault();
            $('#confirm-del-msg').remove();
        });
        $('#yes_del').bind('click', function(event) {
            event.preventDefault();
            $('#confirm-del-msg').remove();
            $.post(l, {list_item: m[1]}, function(response) {
                if (response.success) {
                    $('#list-id-'+m[1]).remove();
                    $('.Grid_content').before('<div id="in-progress">'+gettext('List item deleted')+'</div>');
                    $('#in-progress').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>')
                    ip = setTimeout(function() {$('#in-progress').remove();}, 15050);
                }else{
                    $('.Grid_content').before('<div id="in-progress">'+gettext('List item could not be deleted')+'</div>');
                    $('#in-progress').append('<div id="dismiss"><a href="#">'+gettext('Dismiss')+'</a></div>')
                    ip = setTimeout(function() {$('#in-progress').remove();}, 15050);
                };
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(ip);$('#in-progress').empty().remove();});
            }, "json");
        });
    };
}

function handlextern(){
    page = $.address.parameter("u");
    if(page){
        window.scrollTo(0,0);
        page = $.trim(page);
        re = /^lists\-[1-2]\-[0-9]+\-dsc|asc\-id|to_address|from_address$/
        if(re.test(page)){
            re = /^lists\-([1-2])\-[0-9]+\-dsc|asc\-id|to_address|from_address$/
            f = page.match(re);
            page = page.replace(/-/g,'/');
            url = '/'+ page + '/';
            fetchPage(url,f[1]);
            return false;
        }else{
            page = $.trim(page);
            re = /^lists\-([1-2])$/
            f = page.match(re);
            if(f){
                page = page.replace(/-/g,'/');
                url = '/'+ page + '/';
                fetchPage(url,f[1]);
                url = url.replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
                $.address.value('?u='+url);
                $.address.history($.address.baseURL() + url);
                return false;
            }
        }
    }
}

function list_nav(){
    window.scrollTo(0,0);
    url = $(this).attr('href').replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
    $.address.value('?u='+url);
    $.address.history($.address.baseURL() + url);
    //$.ajaxSetup({'cache':false});
    $.getJSON($(this).attr('href'),lists_from_json);
    return false;
}

function jsize_lists(){
    $('#my-spinner').ajaxStart(ajax_start).ajaxStop(ajax_stop).ajaxError(ajax_error);
    $('#add-item').hide();
    $('#paginator span a').bind('click',list_nav); 
    $.address.externalChange(handlextern);
    $('div.Grid_heading ~ div a').bind('click',confirm_delete);
    $('div.Grid_heading div a').bind('click',list_nav);
    $('#list-link').bind('click',getPage);
    $('#lists_filter_form').submit(submitForm);
}

$(document).ready(jsize_lists);

