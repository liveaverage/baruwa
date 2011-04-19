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
function getTaskStatus(){
    $.getJSON(location.url, function(json, textStatus) {
      if (!json.finished) {
          $('#status').text(json.status);
          $('#percent').text(json.completed);
          $("#progressbar").reportprogress(json.completed);
      }else{
          //build
          var rows = [], count = 0, html = '', img;
          $.each(json.results, function(index, val) {
              if (val.errors.length) {
                  img = '<img src="' + media_url + 'imgs/failed.png" alt="FAILED" />';
              }else{
                  img = '<img src="' + media_url + 'imgs/passed.png" alt="OK" />';
              };
            rows[count++] = '<div class="LightBlue_div">';
            rows[count++] = '<div class="quaran_task_status_row">' + img + '</div>';
            rows[count++] = '<div class="quaran_task_id_row">';
            rows[count++] = '<a href="' + link_url + '/view/' + val.message_id + '/">' + val.message_id + '</a></div>';
            rows[count++] = '<div class="quaran_task_msg_row">';
            if (val.errors.length) {
                for(itr = 0; itr < val.errors.length; itr++){
                    rows[count++] = val.errors[itr]+'<br />';
                }
            }else{
                rows[count++] = gettext('The task was completed successfully.');
            };
            rows[count++] = '</div></div>';
          });
          if (!rows.length) {
              html = '<div class="LightBlue_div"><div class="spanrow">' + gettext("No items processed") + '</div></div>';
          }else{
              html = rows.join('');
          };
          $("div.Grid_heading ~ div").remove();
          $("div.Grid_heading").after(html);
          if(auto_refresh){
              clearInterval(auto_refresh);
          };
      };
    });
    
}

var auto_refresh;
$(document).ready(function() {
    $('#progbar').html('<div id="progressbar"></div>');
    auto_refresh = setInterval(getTaskStatus, 5000);
});
