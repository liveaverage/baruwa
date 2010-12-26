function ajax_start(){
    $(this).append(gettext('&nbsp;Processing...')).show();
    if ($('#in-progress').length) {
        $('#in-progress').remove();
    };
    $('#Footer_container').after(loading_msg);
}

function ajax_stop(){
    $(this).empty().hide();
    $('#loading_message').remove();
}

function ajax_error(event, request, settings){
    if(request.status == 200){
        location.href=settings.url;
    }else{
        $(this).empty().append('<span class="ajax_error">'+gettext('Error connecting to server. check network!')+'</span>').show();
        $('.Grid_heading').before('<div id="ajax-error-msg" class="ui-state-highlight">'+gettext('Server error')+'</div>');
        setTimeout(function() {
            $('#ajax-error-msg').empty().remove();
        }, 3900);
    }
    $('#loading_message').remove();
}

function navigate(){
    window.scrollTo(0,0);
    url = $(this).attr('href').replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
    $.address.value('?u='+url);
    $.address.history($.address.baseURL() + url);
    $.getJSON($(this).attr('href'),page_from_json);
    return false;
}

function paginate(){
    fmt = gettext('Showing page %(page)s of %(pages)s pages.');
    data = {'page':rj.page, 'pages':rj.pages}
    tmp = interpolate(fmt, data, true);
    $('#heading').empty().append('Accounts :: '+tmp);
    $.address.title('Accounts :: '+tmp);
    count = 0;
    row = [];
    row[count++] = tmp;
    if(rj.show_first){
       row[count++] = '<span><a href="/'+rj.app+'/1/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/first_pager.png" alt="First"/></a></span>';
       row[count++] = '<span>.....</span>';
    }
    if(rj.has_previous){
       row[count++] = '<span><a href="/'+rj.app+'/'+rj.previous+'/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/previous_pager.png" alt="Previous"/></a></span>';
    }
    $.each(rj.page_numbers,function(itr,lnk){
       li = '/'+rj.app+'/'+lnk+'/'+rj.direction+'/'+rj.order_by+'/';
       if(rj.page == lnk){
          row[count++] = '<span><b>'+lnk+'</b>&nbsp;</span>';
       }else{
          row[count++] = '<span><a href="'+li+'">'+lnk+'</a>&nbsp;</span>'; 
       }
    });
    if(rj.has_next){
       row[count++] = '<span><a href="/'+rj.app+'/'+rj.next+'/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/next_pager.png" alt="Next"/></a></span>';
    }
    if(rj.show_last){
       row[count++] = '<span>......</span>';
       row[count++] = '<a href="/'+rj.app+'/last/'+rj.direction+'/'+rj.order_by+'/"><img src="/static/imgs/last_pager.png" alt="Last"/></a></span>';
    }
    $('#paginator').html(row.join(''));
    $('#paginator span a').bind('click',navigate);
}

function confirm_delete(event){
    event.preventDefault();
    $(this).blur();
    re = /\/accounts\/user\/delete\/([0-9]+)/
    l = $(this).attr('href');
    m = l.match(re)
    if (m) {
        del_warning = [];
        count = 0;
        del_warning[count++] = '<div id="confirm-del-msg">';
        del_warning[count++] = '<div id="confirm-del-info">';
        del_warning[count++] = gettext('This will delete the account ');
        del_warning[count++] = gettext('and all associated data. This action is not reversible');
        del_warning[count++] = '</div>';
        del_warning[count++] = '<div id="confirm-del-buttons">';
        del_warning[count++] = gettext('Do you wish to continue ?');
        del_warning[count++] = '&nbsp;<input type="button" value="Yes" id="yes_del" />&nbsp;';
        del_warning[count++] = '<input type="button" value="No" id="no_del" />'
        del_warning[count++] = '</div>';
        del_warning[count++] = '</div>'
        if ($('#confirm-del-msg').length) {
            $('#confirm-del-msg').remove();
        };
        $('#account-id-'+m[1]).after(del_warning.join(''));
        $('#no_del').bind('click', function(event) {
            event.preventDefault();
            $('#confirm-del-msg').remove();
        });
        $('#yes_del').bind('click', function(event) {
            event.preventDefault();
            $('#confirm-del-msg').remove();
            $.post(l, {id: m[1]}, function(response) {
                if (response.success) {
                    $('#account-id-'+m[1]).remove();
                    $('.Grid_content').before('<div id="in-progress">'+response.html+'</div>');
                    $('#in-progress').append('<div id="dismiss"><a href="#">gettext('Dismiss')</a></div>')
                    ip = setTimeout(function() {$('#in-progress').remove();}, 15050);
                }else{
                    $('.Grid_content').before('<div id="in-progress">'+response.html+'</div>');
                    $('#in-progress').append('<div id="dismiss"><a href="#">gettext('Dismiss')</a></div>')
                    ip = setTimeout(function() {$('#in-progress').remove();}, 15050);
                };
                $('#dismiss a').click(function(event){event.preventDefault();clearTimeout(ip);$('#in-progress').empty().remove();});
            }, "json");
        });
    };
}

function page_from_json(data){
    if (data) {
        rj = data.paginator;
        row = [];
        count = 0;
        css = 'DarkGray';
        $.each(data.items, function(i, n) {
            if(css == 'LightBlue'){
                css = 'LightGray';
            }else{
                css = 'LightBlue';
            }
            if (n.is_superuser) {
                img = '<img src="/static/imgs/user_red.png" alt="x" title="View account" />';
            }else{
                img = '<img src="/static/imgs/user.png" alt="x" title="View account" />';
            };
            row[count++] = '<div id="account-id-'+n.id+'" class="'+css+'_div">';
            row[count++] = '<div class="hash"><a href="/accounts/user/'+n.id+'/">'+img+'</a></div>';
            row[count++] = '<div class="Users_username">'+n.username+'</div>';
            row[count++] = '<div class="Users_fullname">'+n.first_name+' '+n.last_name+'</div>';
            row[count++] = '<div class="Users_email">'+n.email+'</div>';
            row[count++] = '<div class="Users_del"><a href="/accounts/user/delete/'+n.id+'/">';
            row[count++] = '<img src="/static/imgs/action_delete.png" alt="Delete" title="Delete" />';
            row[count++] = '</a></div></div>';
        });
        if(row.length){
            $("div.Grid_heading").siblings('div').remove();
            $("div.Grid_heading").after(row.join(''));
        }else{
            $("div.Grid_heading").siblings('div').remove();
            $("div.Grid_heading").after('<div class="LightBlue_div"><div class="spanrow">'+gettext('No accounts at the moment')+'</div></div>');
        }
        $('div.Users_del a').bind('click',confirm_delete);
        paginate();
    }
}

function handlextern(){
    page = $.address.parameter("u");
    if(page){
        window.scrollTo(0,0);
        page = $.trim(page);
        re = /^accounts\-[0-9]+\-dsc|asc\-id|username|email$/
        if(re.test(page)){
            page = page.replace(/-/g,'/');
            url = '/'+ page + '/';
            $.get(url, function(response){
                page_from_json(response);
            }, "json");   
        }
    }
    return false;
}

function jsize_page(){
    $('#my-spinner').ajaxStart(ajax_start).ajaxStop(ajax_stop).ajaxError(ajax_error);
    $('#paginator span a').bind('click',navigate);
    $.address.externalChange(handlextern);
    $('div.Users_del a').bind('click',confirm_delete);
}
var loading_msg = '<div id="loading_message"><div id="loading"><img src="/static/imgs/ajax-loader.gif" alt="loading"/><br/><b>'+gettext('Processing')+'</b></div></div>';
$(document).ready(jsize_page);