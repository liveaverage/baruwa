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
        rows = '';
        len = data.items.length;
        len --;
        $.each(data.items,function(i,n){
            //build html rows
            to = '';
            row = '';
            c = '';
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
                c =  'infested';
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
            row += '<td id="first-t">[<a href="/messages/'+n.id+'/">&nbsp;&nbsp;</a>]</td>';
            row += '<td>'+n.timestamp+'</td><td>'+from+'</td><td>'+to+'</td>';
            row += '<td>'+subject+'</td><td>'+filesizeformat(n.size)+'</td>';
            row += '<td>'+n.sascore+'</td><td>'+mstatus+'</td></tr>';
            if(c != ''){
                row = '<tr class="'+stripHTML(c)+'">'+row;
            }else{
                row = '<tr>'+row;
            }
            rows += row;
        });
        if(rows == ''){
            if(full_messages_listing){
                rows = '<tr><td colspan="8" class="align_center">No records returned</td></tr>';
                $("#recent tbody").empty().append(rows);
            }
        }else{
            remove_rows = '';
            if(full_messages_listing){
                $("#recent tbody").empty().append(rows);
            }else{
                if(len == 49){
                    $("#recent tbody").empty().append(rows);
                }else{
                    remove_rows = (48 - len);
                    $("#recent tbody tr:gt("+remove_rows+")").remove();
                    $("#recent tbody").prepend(rows);
                }
            }
        }
    }else{
        $("#search-area").empty().append('Empty response from server. check network!');
    }
}

