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

function en_history(){
    url = $(this).attr('href').replace(/\//g, '-').replace(/^-/, '').replace(/-$/,'');
    $.address.value('?u='+url);
    $.address.history($.address.baseURL() + url);
    window.scrollTo(0,0);
    $('#Footer_container').after(loading_msg);
    $.getJSON($(this).attr('href'),buildhtml);
    return false;
}

function handlextern(){
   page = $.address.parameter("u");
   if(page){
        page = $.trim(page);
        re = /^web\-visits\-full|url|virus|search\-[0-9]+|last\-dsc|asc\-id|date|hostname|username|site|category|size$/;
        if(re.test(page)){
            page = page.replace(/-/g,'/');
            url = '/'+ page + '/';
            window.scrollTo(0,0);
            $('#Footer_container').after(loading_msg);
            $.getJSON(url,buildhtml);
            return false;
        }
   }
}

function paginate(){
   fmt = gettext('Showing page %(page)s of %(pages)s pages.');
   data = {'page':rj.page, 'pages':rj.pages}
   tmp = interpolate(fmt, data, true);
   li='',col='',tmpl='';

   if(rj.show_first){
        if(rj.direction){
            li=visits_base_url+rj.view_type+'/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li=visits_base_url+rj.view_type+'/'+rj.order_by+'/';
        }
        tmp +='<span><a href="'+li+'"><img src="'+media_url+'common/imgs/first_pager.png" alt="First"/></a></span>';
        tmp +='<span>.....</span>';
   }
   if(rj.has_previous){
        if(rj.direction){
            li=visits_base_url+rj.view_type+'/'+rj.previous+'/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li=visits_base_url+rj.view_type+'/'+rj.previous+'/'+rj.order_by+'/';
        }
        tmp +='<span><a href="'+li+'"><img src="'+media_url+'common/imgs/previous_pager.png" alt="Previous"/></a></span>';
   }
   $.each(rj.page_numbers,function(itr,lnk){
        if(rj.page == lnk){ 
            tmp +='<span><b>'+lnk+'</b>&nbsp;</span>';
        }else{
            if(rj.direction){
                li=visits_base_url+rj.view_type+'/'+lnk+'/'+rj.direction+'/'+rj.order_by+'/';
            }else{
                li=visits_base_url+rj.view_type+'/'+lnk+'/'+rj.order_by+'/';
            }
            tmp +='<span><a href="'+li+'">'+lnk+'</a>&nbsp;</span>';
        }
   });
   if(rj.has_next){
        if(rj.direction){
            li=visits_base_url+rj.view_type+'/'+rj.next+'/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li=visits_base_url+rj.view_type+'/'+rj.next+'/'+rj.order_by+'/';
        }
        tmp +='<span><a href="'+li+'"><img src="'+media_url+'common/imgs/next_pager.png" alt="Next"/></a></span>';
   }
   if(rj.show_last){
        if(rj.direction){
            li=visits_base_url+rj.view_type+'/last/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li=visits_base_url+rj.view_type+'/last/'+rj.order_by+'/';
        }
        tmp +='<span>......</span>';
        tmp +='<a href="'+li+'"><img src="'+media_url+'common/imgs/last_pager.png" alt="Last"/></a></span>';
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
    $.address.title('.:. Baruwa :: ' + translted);
    $(this).html(tmp);
    $('#paginator a').bind('click',en_history);
    $('.Grid_heading div a').bind('click',en_history);
    $('#sub-menu-links .ajfy a').bind('click',en_history);
    $('#loading_message').remove();
}

function jsize_page(){
    full_visits_listing = true;
    $('#paginator a').bind('click',en_history);
    $('.Grid_heading div a').bind('click',en_history);
    $('#sub-menu-links .ajfy a').bind('click',en_history);
    $("#paginator").ajaxStop(paginate).ajaxError(function(event, request, settings){
        if(request.status == 200){
            location.href=settings.url;
        }else{
            $('#loading_message').remove();
        }
    });
    $.address.externalChange(handlextern);
}
var loading_msg = '<div id="loading_message"><div id="loading"><img src="'+media_url+'common/imgs/ajax-loader.gif" alt="loading"/><br/><b>'+gettext('Loading')+'</b></div></div>';
$(document).ready(jsize_page);
