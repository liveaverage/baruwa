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
    $.address.title(tmp);
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
    $('#top-pagination').html(tmp);
    $('#top-pagination span a').bind('click',list_nav);
    $('#paginator span a').bind('click',list_nav); 
    $('th a').bind('click',list_nav);
    window.scrollTo(0,0);
}

function lists_from_json(data){
    if(data){
        rj = data.paginator;
        $('#lists tbody').empty(); 
        $.each(data.items,function(i,n){
            link = $("<a/>").attr('href','/lists/delete/'+rj.list_kind+'/'+n.id+'/').html('Delete');
            $('#lists tbody').append('<tr class="lists"><td class="lists first-t">'+n.id+'</td><td class="lists first-t">'+n.to_address+'</td><td class="lists first-t">'+n.from_address+'</td><td class="lists first-t"><a href="/lists/delete/'+rj.list_kind+'/'+n.id+'/">Delete</a></td></tr>');
        });
    }
}

function handlextern(){
    page = $.address.parameter("u");
    if(page){
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
    url = $(this).attr('href').replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
    $.address.value('?u='+url);
    $.address.history($.address.baseURL() + url);
    $('#top-pagination').empty();
	$('#top-pagination').append($("<img/>").attr("src","/static/imgs/loader.gif")).append('&nbsp;Processing........');
    $.getJSON($(this).attr('href'),lists_from_json);
    return false;
}

function jsize_lists(){
    $('#paginator span a').bind('click',list_nav); 
    $('#top-pagination span a').bind('click',list_nav); 
    $('th a').bind('click',list_nav);
    $('#paginator').ajaxStop(paginate);
    $('#top-pagination').ajaxError(function(){
	    $(this).empty();
	    $(this).append('<span class="ajax_error">Error connecting to server. check network!</span>');
    });
    $.address.externalChange(handlextern);
}

$(document).ready(jsize_lists);

