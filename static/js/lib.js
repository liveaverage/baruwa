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
        theTable.fnClearTable(0);
        rj = data.paginator;
        var to;
        var tmp;
        $.each(data.items,function(i,n){
            //build html rows
            to = '';
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
            }
            if(n.virusinfected || n.nameinfected || n.otherinfected){
                mstatus = 'Infected';
            }
            if(!(n.isspam) && !(n.virusinfected) && !(n.nameinfected) && !(n.otherinfected)){
                mstatus = 'Clean';
            }
            if(n.spamwhitelisted){
                mstatus = 'WL';
            }
            if(n.spamblacklisted){
                mstatus = 'BL';
            }
            theTable.fnAddData(['<td id="first-t">[<a href="/messages/'+n.id+'/">&nbsp;&nbsp;</a>]</td>','<td>'+n.timestamp+'</td>','<td>'+from+'</td>','<td>'+to+'</td>','<td>'+stripHTML(n.subject)+'</td>','<td>'+filesizeformat(n.size)+'</td>','<td>'+n.sascore+'</td>','<td>'+mstatus+'</td>']);

        });
        //theTable.fnDraw();
    }else{
        $("#search-area").empty();
        $("#search-area").append('Empty response from server. check network!');
    }
}

function format_rows(nRow, aData, iDisplayIndex){
	$('td:eq(0)',nRow).addClass('first-t'); 
	var ts = $.trim(aData[7]);
	var ss = $.trim(aData[6]);
	ts = $(ts).text();
	ss = $(ss).text();
	if(ts == 'Spam'){
		if(ss >= highscore){
			$(nRow).addClass('highspam');
		}else{
			$(nRow).addClass('spam');
		}
	}
	if(ts == 'WL'){
		$(nRow).addClass('whitelisted');
	}
	if(ts == 'BL'){
		$(nRow).addClass('blacklisted');
	}
	if(ts == 'Infected'){
		$(nRow).addClass('infested');
	}
	if(ts == 'Clean' && ss == 'None'){
		$('td:eq(7)',nRow).text('NS')
	}
	return nRow;
}


