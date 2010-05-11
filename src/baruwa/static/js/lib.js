function wordwrap(str,width,brk,cut) {
    brk = brk || '<br/>\n';
    width = width || 75;
    cut = cut || false;
    if (!str) { return str; }
    var regex = '.{1,' +width+ '}(\\s|$)' + (cut ? '|.{' +width+ '}|.+$' : '|\\S+?(\\s|$)');
    return str.match( RegExp(regex, 'g') ).join( brk );
}
                             
function stripHTML(string) { 
    if(string){
        return string.replace(/<(.|\n)*?>/g, ''); 
    }else{
        return '';
    }
}

function lastupdatetime(){
    var ct = new Date();
    var year,mon,day,hour,min,sec,time;
    year = ct.getFullYear();
    mon = ct.getMonth()+1;
    if(mon < 10){
        mon = '0'+mon;
    }
    day = ct.getDate();
    hour = ct.getHours();
    min = ct.getMinutes();
    sec = ct.getSeconds();
    if(sec < 10){
        sec = '0'+sec;
    }
    if(min < 10){
        min = '0'+min;
    }
    time = year+'-'+mon+'-'+day+' '+hour+':'+min+':'+sec;
    return time;
}

/* based on 
http://www.elctech.com/snippets/convert-filesize-bytes-to-readable-string-in-javascript 
*/
function filesizeformat(bytes){
    var s = ['bytes', 'kb', 'MB', 'GB', 'TB', 'PB'];
    var e = Math.floor(Math.log(bytes)/Math.log(1024));
    return (bytes/Math.pow(1024, Math.floor(e))).toFixed(1)+" "+s[e];
}

function stringtonum(n){ 
    return (typeof(n) == 'number') ? new Number(n) : NaN; 
} 

function json2html(data){
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
            if(n.isspam && !(n.virusinfected) && !(n.nameinfected) && !(n.otherinfected)){
                mstatus = 'Spam';
                if(n.ishighspam){
                    c =  'highspam';
                }else{
                    c =  'spam';
                }
            }
            if(n.virusinfected || n.nameinfected || n.otherinfected){
                mstatus = 'Infected';
                c =  'infected';
            }
            if(!(n.isspam) && !(n.virusinfected) && !(n.nameinfected) && !(n.otherinfected)){
                mstatus = 'Clean';
            }
            if(n.spamwhitelisted){
                mstatus = 'WL';
                c =  'whitelisted';
            }
            if(n.spamblacklisted){
                mstatus = 'BL';
                c =  'blacklisted';
            }
            rows[count++] = '<div class="'+stripHTML(c)+'_div">';
            rows[count++] = '<div class="'+stripHTML(c)+'_Date_Time"><a href="/messages/'+n.id+'/">'+n.timestamp+'</a></div>';
            rows[count++] = '<div class="'+stripHTML(c)+'_From_heading"><a href="/messages/'+n.id+'/">'+from+'</a></div>';
            rows[count++] = '<div class="'+stripHTML(c)+'_To_heading"><a href="/messages/'+n.id+'/">'+to+'</a></div>';
            rows[count++] = '<div class="'+stripHTML(c)+'_Subject_heading"><a href="/messages/'+n.id+'/">'+subject+'</a></div>';
            rows[count++] = '<div class="'+stripHTML(c)+'_Size_heading"><a href="/messages/'+n.id+'/">'+filesizeformat(n.size)+'</a></div>';
            rows[count++] = '<div class="'+stripHTML(c)+'_Score_heading"><a href="/messages/'+n.id+'/">'+n.sascore+'</a></div>';
            rows[count++] = '<div class="'+stripHTML(c)+'_Status_heading"><a href="/messages/'+n.id+'/">'+mstatus+'</a></div>';
            rows[count++] = '</div>';
        });
        if(!rows.length){
            if(full_messages_listing){
                rows = '<div class="spanrow">No records returned</div>';
                $("div.Grid_heading").siblings('div').remove();
                $("div.Grid_heading").after(rows);
            }
        }else{
            if(full_messages_listing){
                $("div.Grid_heading").siblings('div').remove();
                $("div.Grid_heading").after(rows.join(''));
            }else{
                if(len == 49){
                    $("div.Grid_heading").siblings('div').remove();
                    $("div.Grid_heading").after(rows.join(''));
                }else{
                    remove_rows = (48 - len);
                    $("div.Grid_heading ~ div:gt("+remove_rows+")").remove();
                    $("div.Grid_heading").after(rows.join(''));
                }
            }
        }
    }else{
        $("#my-spinner").empty().append('Empty response from server. check network!');
    }
}

function confirm_delete(event){
    link = $(this).attr('href');
    link = $.trim(link);
    //re = /([\w!#$%&'*+/=?`{|}~^-]+(?:\.[!#$%&'*+/=?`{|}~^-]+)*@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}|(?:[A-Z0-9-]+\.)+[A-Z]{2,6})$/
    parts = link.split('/');
    event.preventDefault();
    $dialog.html('Delete filter item Y/N');
    $dialog.dialog('option','buttons',{
        'Delete': function(){
            $(this).dialog('close');
            id = parts[6];
            $.get(link,function(response){
                if(response.success == 'True'){
                    $('#fid_'+id).empty().remove();
                    if(!$('div.Grid_heading ~ div').length){
                        $('div.Grid_heading').after('<div class="spanrow">No filters configured</div>');
                    }
                }else{
                    window.scroll(0,0);
                    if($('#in-progress').length){$('#in-progress').empty().remove();}
                    $('.Grid_content').before('<div id="in-progress">'+response.html+'</div>');
                    setTimeout(function() {$('#in-progress').remove();}, 15050);
                }
            },'json');
        },Cancel: function(){
            $(this).dialog('close');
        }
    });
    $dialog.dialog('open');
}

