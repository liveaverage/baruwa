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
function toplinkize(direction,view_type,field_name,quarantine_type){
    var tmp = '';
    if(direction == 'dsc'){
        tmp = ' <a href="/messages/'+view_type+'/asc/'+field_name+'/">&uarr;</a>';
    }else{
        tmp = ' <a href="/messages/'+view_type+'/dsc/'+field_name+'/">&darr;</a>';
    }
    if (view_type == 'quarantine' && quarantine_type) {
        tmp = tmp.replace(/quarantine\//g,'quarantine/'+quarantine_type+'/');
    };
    return tmp;
}

function en_history(){
    url = $(this).attr('href').replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
    $.address.value('?u='+url);
    $.address.history($.address.baseURL() + url);
    window.scrollTo(0,0);
    if (url == 'messages-quarantine') {
        $('#sub-menu-links ul li').remove();
        var qlinks = ['/messages/quarantine/', '/messages/quarantine/spam/', '/messages/quarantine/policyblocked/'];
        var qtexts = [gettext('Full quarantine'), gettext('Spam'), gettext('Non Spam')];
        var mylinks = [];
        for (var i=0; i < qlinks.length; i++) {
            mylinks[i] = '<li><a href="'+qlinks[i]+'">'+qtexts[i]+'</a></li>';
        };
        $('#sub-menu-links ul').append(mylinks.join(''));
    };
    $('#Footer_container').after(loading_msg);
    $.getJSON($(this).attr('href'),json2html);
    return false;
}

function handlextern(){
   page = $.address.parameter("u");
   if(page){
        page = $.trim(page);
        re = /^messages\-quarantine|full|quarantine\-spam|quarantine\-policyblocked\-[0-9]+|last\-dsc|asc\-timestamp|to_address|from_address|subject|size|sascore$/;
        if(re.test(page)){
            page = page.replace(/-/g,'/');
            url = '/'+ page + '/';
            window.scrollTo(0,0);
            $('#Footer_container').after(loading_msg);
            $.getJSON(url,json2html);
            return false;
        }
   }
}

function paginate(){
   tmp='Showing page '+rj.page+' of '+rj.pages+' pages. ';
   li='',col='',tmpl='';

   if(rj.show_first){
        if(rj.direction){
            li='/messages/'+rj.view_type+'/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li='/messages/'+rj.view_type+'/'+rj.order_by+'/';
        }
        if (rj.view_type == 'quarantine' && rj.quarantine_type) {
            li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
        };
        tmp +='<span><a href="'+li+'"><img src="/static/imgs/first_pager.png" alt="First"/></a></span>';
        tmp +='<span>.....</span>';
   }
   if(rj.has_previous){
        if(rj.direction){
            li='/messages/'+rj.view_type+'/'+rj.previous+'/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li='/messages/'+rj.view_type+'/'+rj.previous+'/'+rj.order_by+'/';
        }
        if (rj.view_type == 'quarantine' && rj.quarantine_type) {
            li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
        };
        tmp +='<span><a href="'+li+'"><img src="/static/imgs/previous_pager.png" alt="Previous"/></a></span>';
   }
   $.each(rj.page_numbers,function(itr,lnk){
        if(rj.page == lnk){ 
            tmp +='<span><b>'+lnk+'</b>&nbsp;</span>';
        }else{
            if(rj.direction){
                li='/messages/'+rj.view_type+'/'+lnk+'/'+rj.direction+'/'+rj.order_by+'/';
            }else{
                li='/messages/'+rj.view_type+'/'+lnk+'/'+rj.order_by+'/';
            }
            if (rj.view_type == 'quarantine' && rj.quarantine_type) {
                li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
            };
            tmp +='<span><a href="'+li+'">'+lnk+'</a>&nbsp;</span>';
        }
   });
   if(rj.has_next){
        if(rj.direction){
            li='/messages/'+rj.view_type+'/'+rj.next+'/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li='/messages/'+rj.view_type+'/'+rj.next+'/'+rj.order_by+'/';
        }
        if (rj.view_type == 'quarantine' && rj.quarantine_type) {
            li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
        };
        tmp +='<span><a href="'+li+'"><img src="/static/imgs/next_pager.png" alt="Next"/></a></span>';
   }
   if(rj.show_last){
        if(rj.direction){
            li='/messages/'+rj.view_type+'/last/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li='/messages/'+rj.view_type+'/last/'+rj.order_by+'/';
        }
        if (rj.view_type == 'quarantine' && rj.quarantine_type) {
            li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
        };
        tmp +='<span>......</span>';
        tmp +='<a href="'+li+'"><img src="/static/imgs/last_pager.png" alt="Last"/></a></span>';
   }
    columns = "timestamp from_address to_address subject size sascore";
    linfo = 'Date_Time#'+gettext('From')+'#'+gettext('To')+'#'+gettext('Subject')+'#'+gettext('Size')+'#'+gettext('Score');
    //alert(linfo);
    carray = columns.split(" ");
    larray = linfo.split("#");
    for(i=0; i< carray.length;i++){
        if(larray[i] == 'Date_Time'){h = gettext('Date/Time');}else{h = larray[i];}
        if(carray[i] == rj.order_by){
            tmpl = toplinkize(rj.direction,rj.view_type,carray[i],rj.quarantine_type);
            $('.'+larray[i]+'_heading').empty().html(h).append(tmpl);
        }else{
            ur = '<a href="/messages/'+rj.view_type+'/'+rj.direction+'/'+carray[i]+'/">'+h+'</a>';
            if (rj.view_type == 'quarantine' && rj.quarantine_type) {
                ur = ur.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
            };
            $('.'+larray[i]+'_heading').empty().html(ur);
        }
    }
    pf = $('#heading small').html();
    fmt = gettext('Showing page %(page)s of %(pages)s pages.');
    transdata = {'page':rj.page, 'pages':rj.pages}
    translted = interpolate(fmt, transdata, true);
    if(pf){
        $('#heading').html(translted+' (<small>'+pf+'</small>)');
    }else{
        $('#heading').html(translted);
    }
    //$.address.title(translted);
    $.address.title('Showing page '+rj.page+' of '+rj.pages+' pages.');
    $(this).html(tmp);
    $('#paginator a').bind('click',en_history);
    $('.Grid_heading div a').bind('click',en_history);
    $('#sub-menu-links ul li a').bind('click',en_history);
    $('#loading_message').remove();
}

function jsize_page(){
    full_messages_listing = true;
    $('#fhl').before($('<a/>').attr({href:'#',id:'filter-toggle'}).html('&darr;&nbsp;'+gettext('Show filters')));
    $('#fhl').hide();
    $('#filter-toggle').bind('click',function(e){
        e.preventDefault();    
        $('#fhl').toggle();
        if($('#fhl').css('display') == 'inline'){
            $(this).html('&uarr;&nbsp;'+gettext('Hide filters')).blur();
        }else{
            $(this).html('&darr;&nbsp;'+gettext('Show filters')).blur();
        }
    });
    $('#paginator a').bind('click',en_history);
    $('.Grid_heading div a').bind('click',en_history);
    $('#sub-menu-links ul li a').bind('click',en_history);
    $("#paginator").ajaxStop(paginate).ajaxError(function(event, request, settings){
        if(request.status == 200){
            location.href=settings.url;
        }else{
            $('#loading_message').remove();
        }
    });
    $.address.externalChange(handlextern);
}
var loading_msg = '<div id="loading_message"><div id="loading"><img src="/static/imgs/ajax-loader.gif" alt="loading"/><br/><b>'+gettext('Loading')+'</b></div></div>';
$(document).ready(jsize_page);
