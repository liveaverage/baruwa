function ajax_start(){
    $(this).append($("<img/>").attr('src','/static/imgs/loader-orig.gif')).append('&nbsp;Processing...');
}

function ajax_stop(){
    $(this).empty();
    if($('#lists-spinner').length){
        $('#lists-spinner').remove();
        $('#pagination_info small').remove();
    }
}

function ajax_error(event, request, settings){
    if(request.status == 200){
        if(settings.url == '/lists/add/'){
            location.href='/lists/';
        }else{
            location.href=settings.url;
        }
    }else{
        $(this).empty();
        $('#pagination_info').empty().append('<span class="ajax_error">Error connecting to server. check network!</span>');
    }
}

function toplinkize(app,direction,field_name){
    var tmp = '';
    if(direction == 'dsc'){
        tmp = ' <a href="/'+app+'/asc/'+field_name+'/">&darr;</a>';
    }else{
        tmp = ' <a href="/'+app+'/dsc/'+field_name+'/">&uarr;</a>';
    }
    return tmp;
}

function paginate(){
    tmp = 'Showing page '+rj.page+' of '+rj.pages+' pages. ';
    $('#pagination_info').html(tmp);
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

    oi = $('#sorting_by').index();
    columns = "id to_address from_address";
    linfo = "# To From"
    carray = columns.split(" ");
    larray = linfo.split(" ");
    $("#sorting_by").html('<a href="/'+rj.app+'/'+rj.direction+'/'+carray[oi]+'/">'+larray[oi]+'</a>').removeAttr('id');
    for(i=0; i< carray.length;i++){
        if(rj.order_by == carray[i]){
            $('#lists th:eq('+i+')').text(larray[i]).attr('id','sorting_by');
            tmpl = toplinkize(rj.app,rj.direction,carray[i]);
            $('#lists th:eq('+i+')').append(tmpl);
            $('#lists_filter_form').attr('action','/'+rj.app+'/'+rj.direction+'/'+carray[i]+'/');
        }else{
            ur = '/'+rj.app+'/'+rj.direction+'/'+carray[i]+'/';
            if($('#lists th:eq('+i+') a').attr('href') != ur){
                $('#lists th:eq('+i+') a').attr('href',ur);
            }
        }
    }
    
    $('#paginator').html(tmp);
    $('#paginator span a').bind('click',list_nav); 
    $('th a').bind('click',list_nav);
}

function lists_from_json(data){
    if(data){
        rj = data.paginator;
        tti = [];
        count = 0;
        $.each(data.items,function(i,n){
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
            tti[count++] = '<tr class="lists" id="list-id-'+n.id+'"><td class="lists first-t">'+n.id+'</td><td class="lists first-t">'+to_address+'</td>';
            tti[count++] = '<td class="lists first-t">'+from_address+'</td><td class="lists first-t">';
            tti[count++] = '<a href="/lists/delete/'+rj.list_kind+'/'+n.id+'/">Delete</a></td></tr>';
        });
        if(tti.length){
            $('#lists tbody').empty().append(tti.join(''));
        }else{
            $('#lists tbody').empty().append('<tr class="lists"><td colspan="4" class="lists align_center">No items at the moment</td></tr>');
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
        $('tbody a').bind('click',confirm_delete);
        paginate();
    }
}

function fetchPage(link,list_type){
    //$.ajaxSetup({'cache':false});
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
        t = $('#pagination_info');
        $('#divider-header h3').html(ct).append(t);
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
    if(found.length == 3){
        event.preventDefault();
        if(found[1] == 1){list = 'Whitelist';}else{list = 'Blacklist';}
        alt = 'Delete '+$("tr#list-id-"+found[2]+" td:eq(2)").text()+' from '+list;
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
                                //'cache':false
                            });
                        }
                    }
                }
                $.get(str,function(response){
                    if(!response.error){
                        lists_from_json(response);
                    }else{
                        window.scroll(0,0);
                        $("#in-progress").html(response.error).fadeIn(50).delay(15000).slideToggle('fast');
                    }
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
                t = $('#pagination_info');
                $('#divider-header h3').html(ct).append(t);
                $('#sub-menu-links ul li:first a').attr({id:'list-link',href:ll,innerHTML:lt});
                $('#lists tbody tr:eq(0)').addClass('whitelisted');
                $("form")[ 0 ].reset();
                $('#add-item').hide();
                $('#add-sep').hide();
                $('#list-add').html('Add to List').blur();
                setTimeout(function(){$('#lists tbody tr:eq(0)').removeClass('whitelisted');},15000);
            }else{
                if($('#aj-form-warning').length > 0){
                    $('#aj-form-warning').html(response.error);
                }else{
                    $('#ins-after').after('&nbsp;<span id="aj-form-warning" class="filter_errors">'+response.error+'</span>');
                }
            }
        },"json");
    $('#submit-button').removeAttr('disabled');
    $('#cancel-button').removeAttr('disabled');
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
    $('th a').bind('click',list_nav);
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
    $('tbody a').bind('click',confirm_delete);
    $('#list-add').bind('click',function(event){
        event.preventDefault();
        if($("#add-item").is(':visible')){
            $('#add-item').hide();
            $('#add-sep').hide();
            $(this).html('Add to List').blur();
            $("form")[0].reset();
            if($('#aj-form-warning').length > 0){$('#aj-form-warning').remove();}
        }else{
            $('#add-item').show();
            $('#add-sep').show();
            $(this).html('Cancel add').blur();
        }
    });
    $('#list-form').submit(handlePost);
    $('#cancel-button').bind('click',function(){
        if($("#add-item").is(':visible')){
            $('#add-item').hide();
            $('#add-sep').hide();
            $('#list-add').html('Add to List').blur();
            $("form")[0].reset();
            if($('#aj-form-warning').length > 0){$('#aj-form-warning').remove();}
        }
    });
    $('#list-link').bind('click',getPage);
    $('#lists_filter_form').submit(submitForm);
}

var $dialog = $('<div></div>');
$(document).ready(jsize_lists);

