// csrf cookie
function getCSRF() {
    var cookieValue = null;
    var name = 'csrftoken';
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    var self = this;
    return cookieValue;
};

function seteditor(){
    if ($('#id_signature_type').val() == 1) {
        var editor = $("#id_signature_content").cleditor()[0];
        editor.$area.insertBefore(editor.$main);
        editor.$area.removeData("cleditor");
        editor.$main.remove();
        $('#id_signature_content').show();  
    }else{
        $('#id_signature_content').cleditor();
    };
}
$(document).ready(function() {
    var uploadform = 	'<form enctype="multipart/form-data" method="post" action="' + fm_url + '">' + 
	                '<input type="hidden" name="csrfmiddlewaretoken" value="' + getCSRF() + '" />' +
					'<p><input type="file" name="handle" /><br>' + 
					'<input type="text" name="newName" style="width:250px; border:solid 1px !important;" /><br>' + 
					'<input type="text" name="action" style="display:none;" value="upload" /><br></p>' + 
					'<input type="submit" name="submit" value="Upload" />' +
					'</form>';
    $('#id_signature_type').change(seteditor);
    if ($('#id_signature_type').val() == 2) {
        $('#id_signature_content').cleditor();
    };
    $('#currimgs .wysiwyg-dialog-close-button').click(function(e){
        e.preventDefault();
        $('#currimgs').hide();
    });
    $('#imgupload .wysiwyg-dialog-close-button').click(function(e){
        e.preventDefault();
        $('#currimgs').hide();
        $('#imgupload').hide();
    });
    $(".wysiwyg-files-action-upload").bind("click", function (e) {
        $('#imgupload .wysiwyg-dialog-content').empty();
        $("<iframe/>", { "class": "wysiwyg-files-upload" }).load(function () {
			var $doc = $(this).contents();
			$doc.find("body").append(uploadform);
			$doc.find("input[type=file]").change(function () {
				var $val = $(this).val();
				$val = $val.replace(/.*[\\\/]/, '');
				$doc.find("input[name=newName]").val($val);
			});
		}).appendTo($('#imgupload .wysiwyg-dialog-content'));
        $('#imgupload').show();
    });
});

