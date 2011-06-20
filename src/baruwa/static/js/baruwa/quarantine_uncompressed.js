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

function buildrows(data){
    if(data){
        rj = data.paginator;
        if(data.items.length){
            last_ts = data.items[0].timestamp;
        }
        var to;
        var tmp;
        rows = [];
        len = data.items.length;
        len --;
        count = 0;
        //status
        $('#smailtotal').empty().append(data.status.baruwa_mail_total);
        $('#sspamtotal').empty().append(data.status.baruwa_spam_total);
        $('#svirustotal').empty().append(data.status.baruwa_virus_total);
        $('#inq').empty().append(data.status.baruwa_in_queue);
        $('#outq').empty().append(data.status.baruwa_out_queue);
        if(data.status.baruwa_status){
            simg = 'active.png';
            alt = 'OK';
        }else{
            simg = 'inactive.png';
            alt = 'FAULTY';
        }
        var statusimg = media_url + 'imgs/' + simg;
        $('#statusimg').attr('src', statusimg).attr('alt', alt);
        //build records table
        $.each(data.items,function(i,n){
            //build html rows
            to = '';
            c = 'LightBlue';
            tmp = n.to_address.split(',');
            for(itr = 0; itr < tmp.length; itr++){
                to += tmp[itr]+'<br />';
            }
            if(n.from_address.length > 30){
                var from = n.from_address.substring(0,29) + '...';
            }else{
                var from = n.from_address;
            }
            s = stripHTML(n.subject);
            if(s.length > 38){
                re = /\s/g;
                if(re.test(s)){
                   subject = wordwrap(s,45); 
                }else{
                    subject = s.substring(0,44) + '...';
                }
            }else{
                subject = s;
            }
            var mstatus = '';
            if(n.spam && !(n.virusinfected) && !(n.nameinfected) && !(n.otherinfected)){
                mstatus = gettext('Spam');
                if(n.highspam){
                    c =  'highspam';
                }else{
                    c =  'spam';
                }
            }
            if(n.virusinfected || n.nameinfected || n.otherinfected){
                mstatus = gettext('Infected');
                c =  'infected';
            }
            if(!(n.spam) && !(n.virusinfected) && !(n.nameinfected) && !(n.otherinfected)){
                mstatus = gettext('Clean');
            }
            if(n.whitelisted && !(n.virusinfected) && !(n.nameinfected) && !(n.otherinfected)){
                mstatus = 'WL';
                c =  'whitelisted';
            }
            if(n.blacklisted){
                mstatus = 'BL';
                c =  'blacklisted';
            }
            if (!n.scaned) {
                mstatus = 'NS';
                c = 'LightGray';
            };
            rows[count++] = '<div class="'+stripHTML(c)+'_div">';
            rows[count++] = '<div class="quaran_select_row"><input type="checkbox" name="message_id" value="'+n.id+'" class="selector" /></div>';
            rows[count++] = '<div class="quaran_date_time_row"><a href="/messages/view/'+n.id+'/">'+n.timestamp+'</a></div>';
            rows[count++] = '<div class="quaran_from_row"><a href="/messages/view/'+n.id+'/">'+from+'</a></div>';
            rows[count++] = '<div class="quaran_to_row"><a href="/messages/view/'+n.id+'/">'+to+'</a></div>';
            rows[count++] = '<div class="quaran_subject_row"><a href="/messages/view/'+n.id+'/">'+subject+'</a></div>';
            rows[count++] = '<div class="quaran_score_row"><a href="/messages/view/'+n.id+'/">'+n.sascore+'</a></div>';
            rows[count++] = '<div class="quaran_status_row"><a href="/messages/view/'+n.id+'/">'+mstatus+'</a></div>';
            rows[count++] = '</div>';
        });
        if(!rows.length){
            rows = '<div class="spanrow">'+gettext('No records returned')+'</div>';
            $("div.Grid_heading ~ div").remove();
            $("div.Grid_heading").after(rows);
        }else{
            $("div.Grid_heading ~ div").remove();
            $("div.Grid_heading").after(rows.join(''));
        }
    }else{
        $("#my-spinner").empty().append(gettext('Empty response from server. check network!'));
    }
}


function toplinkize(direction,field_name,quarantine_type){
    var tmp = '';
    if(direction == 'dsc'){
        tmp = ' <a href="/messages/quarantine/asc/'+field_name+'/">&uarr;</a>';
    }else{
        tmp = ' <a href="/messages/quarantine/dsc/'+field_name+'/">&darr;</a>';
    }
    if (quarantine_type) {
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
    $.getJSON($(this).attr('href'),buildrows);
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
            $.getJSON(url,buildrows);
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
            li='/messages/quarantine/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li='/messages/quarantine/'+rj.order_by+'/';
        }
        if (rj.quarantine_type) {
            li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
        };
        tmp +='<span><a href="'+li+'"><img src="'+media_url+'imgs/first_pager.png" alt="First"/></a></span>';
        tmp +='<span>.....</span>';
   }
   if(rj.has_previous){
        if(rj.direction){
            li='/messages/quarantine/'+rj.previous+'/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li='/messages/quarantine/'+rj.previous+'/'+rj.order_by+'/';
        }
        if (rj.quarantine_type) {
            li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
        };
        tmp +='<span><a href="'+li+'"><img src="'+media_url+'imgs/previous_pager.png" alt="Previous"/></a></span>';
   }
   $.each(rj.page_numbers,function(itr,lnk){
        if(rj.page == lnk){ 
            tmp +='<span><b>'+lnk+'</b>&nbsp;</span>';
        }else{
            if(rj.direction){
                li='/messages/quarantine/'+lnk+'/'+rj.direction+'/'+rj.order_by+'/';
            }else{
                li='/messages/quarantine/'+lnk+'/'+rj.order_by+'/';
            }
            if (rj.quarantine_type) {
                li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
            };
            tmp +='<span><a href="'+li+'">'+lnk+'</a>&nbsp;</span>';
        }
   });
   if(rj.has_next){
        if(rj.direction){
            li='/messages/quarantine/'+rj.next+'/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li='/messages/quarantine/'+rj.next+'/'+rj.order_by+'/';
        }
        if (rj.quarantine_type) {
            li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
        };
        tmp +='<span><a href="'+li+'"><img src="'+media_url+'imgs/next_pager.png" alt="Next"/></a></span>';
   }
   if(rj.show_last){
        if(rj.direction){
            li='/messages/quarantine/last/'+rj.direction+'/'+rj.order_by+'/';
        }else{
            li='/messages/quarantine/last/'+rj.order_by+'/';
        }
        if (rj.quarantine_type) {
            li = li.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
        };
        tmp +='<span>......</span>';
        tmp +='<a href="'+li+'"><img src="'+media_url+'imgs/last_pager.png" alt="Last"/></a></span>';
   }
    columns = "timestamp from_address to_address subject sascore";
    linfo = gettext('Date/Time')+'#'+gettext('From')+'#'+gettext('To')+'#'+gettext('Subject')+'#'+gettext('Score');
    style = ".quaran_date_time_heading .quaran_from_heading .quaran_to_heading .quaran_subject_heading .quaran_score_heading";
    //alert(linfo);
    carray = columns.split(" ");
    larray = linfo.split("#");
    styles = style.split(" ");
    for(i=0; i< carray.length;i++){
        h = larray[i];
        if(carray[i] == rj.order_by){
            tmpl = toplinkize(rj.direction,carray[i],rj.quarantine_type);
            $(styles[i]).empty().html(h).append(tmpl);
        }else{
            ur = '<a href="/messages/quarantine/'+rj.direction+'/'+carray[i]+'/">'+h+'</a>';
            if (rj.quarantine_type) {
                ur = ur.replace(/quarantine\//g,'quarantine/'+rj.quarantine_type+'/');
            };
            $(styles[i]).empty().html(ur);
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
    $.address.title('.:. Baruwa :: ' + translted);
    $(this).html(tmp);
    $('#allchecker').attr('checked', false);
    $('#paginator a').bind('click',en_history);
    $('.Grid_heading div a').bind('click',en_history);
    $('#sub-menu-links ul li a').bind('click',en_history);
    $('#loading_message').remove();
}

function jsize_page(){
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
    $('#allchecker').attr('checked', false);
    $('#allchecker').bind('click', function(){
        $('.selector').attr('checked', this.checked);
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
var loading_msg = '<div id="loading_message"><div id="loading"><img src="'+media_url+'imgs/ajax-loader.gif" alt="loading"/><br/><b>'+gettext('Loading')+'</b></div></div>';
$(document).ready(jsize_page);
