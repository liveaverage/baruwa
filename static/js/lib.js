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
        var to;
        var tmp;
        rows = '';
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
            row += '<td>'+stripHTML(n.subject)+'</td><td>'+filesizeformat(n.size)+'</td>';
            row += '<td>'+n.sascore+'</td><td>'+mstatus+'</td></tr>';
            if(c != ''){
                row = '<tr class="'+stripHTML(c)+'">'+row;
            }else{
                row = '<tr>'+row;
            }
            rows += row;
        });
        $("#recent tbody").empty();
        if(rows == ''){
            rows = '<tr><td colspan="8" class="align_center">No records returned</td></tr>';
        }
        $("#recent tbody").append(rows);
    }else{
        $("#search-area").empty();
        $("#search-area").append('Empty response from server. check network!');
    }
}

