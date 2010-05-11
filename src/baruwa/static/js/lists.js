function ajax_start(){
    $(this).append($("<img/>").attr('src','/static/imgs/loader-orig.gif')).append('&nbsp;Processing...');
    $('div.ui-dialog-titlebar').append($("<img/>").attr('src','/static/imgs/loader.gif'));
}

function ajax_stop(){
    $(this).empty();
    if($('#lists-spinner').length){
        $('#lists-spinner').remove();
    }
    $('div.ui-dialog-titlebar img').remove();
}

function ajax_error(event, request, settings){
    if(request.status == 200){
        if(settings.url == '/lists/add/'){
            location.href='/lists/';
        }else{
            location.href=settings.url;
        }
    }else{
        $(this).empty().append('<span class="ajax_error">Error connecting to server. check network!</span>');
    }
    $('div.ui-dialog-titlebar img').remove();
}

function toplinkize(app,direction,field_name){
    var tmp = '';
    if(direction == 'dsc'){
        tmp = ' <a href="/'+app+'/asc/'+field_name+'/">&uarr;</a>';
    }else{
        tmp = ' <a href="/'+app+'/dsc/'+field_name+'/">&darr;</a>';
    }
    return tmp;
}

function paginate(list_type){
    if(list_type == '1'){
        lt = 'Whitelist :: ';
    }else{
        lt = 'Blacklist :: ';
    }
    tmp = 'Showing page '+rj.page+' of '+rj.pages+' pages. ';
    $('#heading').empty().append(lt+tmp);
    $.address.title('Baruwa :: List management '+tmp);
    li = '';

    if(rj.show_first){
        tmp +='<span><a href="/'+rj.app+'/1/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/first_pager.png" alt="First"/></a></span>';
        tmp +='<span>.....</span>';
    }
    if(rj.has_previous){
        tmp +='<span><a href="/'+rj.app+'/'+rj.previous+'/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/previous_pager.png" alt="Previous"/></a></span>';
    }
    $.each(rj.page_numbers,function(itr,lnk){
        li = '/'+rj.app+'/'+lnk+'/'+rj.direction+'/'+rj.order_by+'/';
        if(rj.page == lnk){
            tmp +='<span><b>'+lnk+'</b>&nbsp;</span>';
        }else{
           tmp +='<span><a href="'+li+'">'+lnk+'</a>&nbsp;</span>'; 
        }
    });
    if(rj.has_next){
        tmp +='<span><a href="/'+rj.app+'/'+rj.next+'/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/next_pager.png" alt="Next"/></a></span>';
    }
    if(rj.show_last){
        tmp +='<span>......</span>';
        tmp +='<a href="/'+rj.app+'/last/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/last_pager.png" alt="Last"/></a></span>';
    }
    columns = "id to_address from_address";
    linfo = "hash To From"
    carray = columns.split(" ");
    larray = linfo.split(" ");
    for(i=0; i< carray.length;i++){
        if(larray[i] == 'hash'){h = '#';}else{h = larray[i];}
        if(rj.order_by == carray[i]){
            tmpl = toplinkize(rj.app,rj.direction,carray[i]);
            $('.Lists_grid_'+larray[i]).empty().html(h).append(tmpl);
            $('#lists_filter_form').attr('action','/'+rj.app+'/'+rj.direction+'/'+carray[i]+'/');
        }else{
            ur = '<a href="/'+rj.app+'/'+rj.direction+'/'+carray[i]+'/">'+h+'</a>';
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
        css = 'DarkGray';
        list_type = '1';
        $.each(data.items,function(i,n){
            list_type = rj.list_kind;
            if(n.from_address == 'default'){
                from_address = 'Any address';
            }else{
                from_address = n.from_address;
            }
            if(n.to_address == 'default'){
                to_address = 'Any address';
            }else{
                to_address = n.to_address;
            }
            link = '<a href="/lists/delete/'+rj.list_kind+'/'+n.id+'/"><img src="/static/imgs/action_delete.png" title="Delete" alt="Delete" /></a>';
            if(n.from_address == '127.0.0.1'){
                if(n.to_address == 'default'){
                    link = '=builtin=';
                }
            }

            if(css == 'LightBlue'){
                css = 'DarkGray';
            }else{
                css = 'LightBlue';
            }

            tti[count++] = '<div class="'+css+'_div">';
            tti[count++] = '<div class="Lists_'+css+'_hash">'+n.id+'</div>';
            tti[count++] = '<div class="Lists_'+css+'_to">'+to_address+'</div>';
            tti[count++] = '<div id="list-id-'+n.id+'" class="Lists_'+css+'_from">'+from_address+'</div>';
            tti[count++] = '<div class="Lists_'+css+'_action">'+link+'</div>';
            tti[count++] = '</div>';
        });
        if(tti.length){
            $("div.Grid_heading").siblings('div').remove();
            $("div.Grid_heading").after(tti.join(''));
        }else{
            $("div.Grid_heading").siblings('div').remove();
            $("div.Grid_heading").after('<div class="LightBlue_div">No items at the moment</div>');
        }
        if(rj.order_by == 'id'){
            $('#filterbox').hide('fast');
        }else{
            $('#filterbox').show('fast');
            if(rj.order_by == 'to_address'){
                $('#filterlabel').html('<b>To:</b>');
            }else{
                $('#filterlabel').html('<b>From:</b>');
            }
        }
        $('div.Grid_heading ~ div a').bind('click',confirm_delete);
        paginate(list_type);
    }
}

function fetchPage(link,list_type){
    $.get(link,function(response){
        lists_from_json(response);
        if(list_type == '1'){
            lt = 'Blacklist';
            ll = '/lists/2/';
            ct = 'Whitelist :: ';
        }else{
            lt = 'Whitelist';
            ll = '/lists/1/';
            ct = 'Blacklist :: ';
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
    $('#id_lists_filter_submit').attr({'disabled':'disabled','value':'Loading'});
    event.preventDefault();
    filter_request = {
        query_type: $("#id_query_type").val(),
        search_for: $("#id_search_for").val()
    };
    link = $("#lists_filter_form").attr("action");
    $.post(link,filter_request,
        function(response){
            lists_from_json(response);
            url = link.replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
            $.address.value('?u='+url);
            $.address.history($.address.baseURL() + url);
        },"json");
    $('#id_lists_filter_submit').removeAttr('disabled').attr('value','Go');
}

function confirm_delete(event) {
    re = /\/lists\/delete\/(\d+)\/(\d+)/
    str = $(this).attr('href');
    found = str.match(re);
    event.preventDefault();
    if(found.length == 3){
        if(found[1] == 1){list = 'Whitelist';}else{list = 'Blacklist';}
        alt = 'Delete '+$("div#list-id-"+found[2]+"").text()+' from '+list;
        $dialog.html(alt);
        $dialog.dialog('option','buttons', {
            'Delete': function() {
                $(this).dialog('close');
                p = $.address.parameter("u");
                if(p){
                    p = $.trim(p);
                    re = /^lists\-([1-2])\-([0-9]+)\-(dsc|asc)\-(id|to_address|from_address)$/
                    f = p.match(re);
                    if(f){
                        if(f.length > 1){
                            $.ajaxSetup({
                                'beforeSend':function(xhr){xhr.setRequestHeader("X-List-Params",p);}
                            });
                        }
                    }
                }
                $.get(str,function(response){
                    window.scroll(0,0);
                    if($('#in-progress').length){clearTimeout(ip);$('#in-progress').empty().remove();}
                    if(!response.error){
                        lists_from_json(response);
                        $('.Grid_content').before('<div id="in-progress">List item deleted</div>');
                        $('#in-progress').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
                        ip = setTimeout(function() {$('#in-progress').remove();}, 15050);
                    }else{
                        $('.Grid_content').before('<div id="in-progress">'+response.html+'</div>');
                        $('#in-progress').append('<div id="dismiss"><a href="#">Dismiss</a></div>')
                        ip = setTimeout(function() {$('#in-progress').remove();}, 15050);
                    }
                    $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(ip);$('#in-progress').empty().remove();});
                },'json');
            },Cancel: function() {
                $(this).dialog('close');
            }
        });
        $dialog.dialog('open');
    }
}

function handlePost(event){
    $('#submit-button').attr('disabled','disabled');
    $('#cancel-button').attr('disabled','disabled');
    $('input').removeClass('ui-state-error');
    event.preventDefault();
    var list_add_request = {
        from_address: $('#id_from_address').val(),
        to_address: $('#id_to_address').val(),
        to_domain: $('#id_to_domain').val(),
        list_type: $('#id_list_type').val()
    };
    $.post('/lists/add/',list_add_request,
        function(response){
            if(!response.error){
                lists_from_json(response);
                if(list_add_request['list_type'] == '1'){
                    lt = 'Blacklist';
                    ll = '/lists/2/';
                    ct = 'Whitelist :: ';
                }else{
                    lt = 'Whitelist';
                    ll = '/lists/1/';
                    ct = 'Blacklist :: ';
                }
                $('#heading').html(ct);
                $('#sub-menu-links ul li:first a').attr({id:'list-link',href:ll,innerHTML:lt});
                $('div.Grid_heading ~ div:eq(0)').addClass('whitelisted_div');
                $('form').clearForm();
                $('#list-add').html('Add to List').blur();
                $('#add-item').dialog('close');
                setTimeout(function(){
                    $('div.Grid_heading ~ div:eq(0)').removeClass('whitelisted_div');
                    $('div.Grid_heading ~ div:eq(0)').addClass('LightBlue_div');
                },15000);
            }else{
                $('#id_'+response.form_field).addClass('ui-state-error');
                if($('#ajax-error-msg').length){clearTimeout(timeout);$('#ajax-error-msg').empty().remove();}
                $('#list-form').before('<div id="ajax-error-msg" class="ui-state-highlight">'+response.error+'</div>');
                timeout = setTimeout(function() {
                    $('#ajax-error-msg').empty().remove();
                }, 3900);
            }
            $('#submit-button').removeAttr('disabled');
            $('#cancel-button').removeAttr('disabled');
        },"json");
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
    //$('th a').bind('click',list_nav);
    $.address.externalChange(handlextern);
    $dialog.html('An error occured !')
        .dialog({
            autoOpen: false,
            resizable: false,
            height:120,
            width: 500,
            modal: true,
            title: 'Please confirm deletion ?',
            closeOnEscape: false,
            open: function(event, ui) {$(".ui-dialog-titlebar-close").hide();},
            draggable: false,
        });
    $('div.Grid_heading ~ div a').bind('click',confirm_delete);
    $('div.Grid_heading div a').bind('click',list_nav);
    $('#list-add').bind('click',function(event){
        event.preventDefault();
        $('#add-item').dialog('open');
        $('input').removeClass('ui-state-error');
        $(this).html('Add to List').blur();
        $('form').clearForm();
    });
    $('#list-form').submit(handlePost);
    $('#cancel-button').bind('click',function(){
        $('#list-add').html('Add to List').blur();
        $('form').clearForm();
        if($('#aj-form-warning').length > 0){$('#aj-form-warning').remove();}
        $('#add-item').dialog('close');
        $('input').removeClass('ui-state-error');
    });
    $('#list-link').bind('click',getPage);
    $('#lists_filter_form').submit(submitForm);
    $("#add-item").dialog({
        autoOpen: false,
        height: 220,
        width: 450,
        modal: true,
        title: 'List an address',
        closeOnEscape: false,
        open: function(event, ui) {$(".ui-dialog-titlebar-close").hide();},
    });

}

var $dialog = $('<div></div>');
$(document).ready(jsize_lists);

