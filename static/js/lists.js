function confirm_delete(event) {
    re = /\/lists\/delete\/(\d+)\/(\d+)/
    str = $(this).attr('href');
    found = str.match(re);
    if(found.length == 3){
        event.preventDefault();
        if(found[1] == 1){list = 'Whitelist';}else{list = 'Blacklist';}
        alt = 'Delete '+$("tr#"+found[2]+" td:eq(2)").text()+' from '+list;
        $dialog.html(alt);
        $dialog.dialog('option','buttons', {
            'Delete': function() {
                window.location.href=str;
                $(this).dialog('close');
            },Cancel: function() {
                $(this).dialog('close');
            }
        });
        $dialog.dialog('open');
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
        }
    }
    
    $(this).html(tmp);
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
            tti[count++] = '<tr class="lists" id="'+n.id+'"><td class="lists first-t">'+n.id+'</td><td class="lists first-t">'+to_address+'</td>';
            tti[count++] = '<td class="lists first-t">'+from_address+'</td><td class="lists first-t">';
            tti[count++] = '<a href="/lists/delete/'+rj.list_kind+'/'+n.id+'/">Delete</a></td></tr>';
        });
        if(tti.length){
            $('#lists tbody').empty().append(tti.join(''));
        }else{
            $('#lists tbody').empty().append('<tr class="lists"><td colspan="4" class="lists first-t">No lists found</td></tr>');
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
    }
}

function handlextern(){
    page = $.address.parameter("u");
    if(page){
        window.scrollTo(0,0);
        page = $.trim(page);
        re = /^lists\-[1-2]\-[0-9]+\-dsc|asc\-id|to_address|from_address$/
        if(re.test(page)){
            page = page.replace(/-/g,'/');
            url = '/'+ page + '/';
            $.getJSON(url,lists_from_json);
            return false;
        }
    }
}

function list_nav(){
    window.scrollTo(0,0);
    url = $(this).attr('href').replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
    $.address.value('?u='+url);
    $.address.history($.address.baseURL() + url);
	$('#pagination_info').append($("<img/>").attr({src:"/static/imgs/loader.gif",id:'lists-spinner'})).append('&nbsp;<small>Processing........</small>');
    $.getJSON($(this).attr('href'),lists_from_json);
    return false;
}

function jsize_lists(){
    $('#paginator span a').bind('click',list_nav); 
    $('th a').bind('click',list_nav);
    $('#paginator').ajaxStop(paginate);
    $('#pagination_info').ajaxError(function(){
	    $(this).empty().append('<span class="ajax_error">Error connecting to server. check network!</span>');
    });
    $.address.externalChange(handlextern);
    $dialog.html('This dialog will show every time!')
        .dialog({
            autoOpen: false,
            resizable: false,
            height:120,
            width: 500,
            modal: true,
            title: 'Please confirm deletion ?',
            closeOnEscape: false,
            open: function(event, ui) {$(".ui-dialog-titlebar-close").hide(); /*$('body').css('overflow', 'hidden');*/},
            //close: function(event, ui) {$('body').css('overflow', 'auto');},
            draggable: false,

        });
    $('tbody a').bind('click',confirm_delete);
}

var $dialog = $('<div></div>');
$(document).ready(jsize_lists);

