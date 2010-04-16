function handleListing(e){
    dojo.require("dojo.NodeList-manipulate");
    e.preventDefault();
    url = dojo.attr(e.target,'href');
    id = dojo.attr(e.target,'id');
    dojo.xhrGet({
        url:url,
        handleAs:'json',
        handle:function(data,args){
            if(typeof data == "error"){
                d = dojo.byId("in-progress");
                d.innerHTML = args;
                d.style.display = "block";
            }else{
                if(data.success == 'True'){
                    d = dojo.byId("in-progress");
                    d.innerHTML = data.html;
                    d.style.display = "block";
                    dojo.query("#"+id).before(id);
                    dojo.destroy(id);
                }else{
                    d = dojo.byId("in-progress");
                    d.innerHTML = data.html;
                    d.style.display = "block";
                }
            }
        }
    });
    setTimeout(function(){dojo.byId("in-progress").style.display = "none";},30000);
}

var formSubmission = function(e){
    dojo.attr("submit_q_request","disabled",true);
    dojo.byId("quarantine_errors").innerHTML = "";
    dojo.create("img",{src:"/static/imgs/loader.gif",alt:"loading"},dojo.byId("ajax_status"))
    dojo.byId("ajax_status").innerHTML += '&nbsp;Processing the request...';
    var release  = 0;
    var todelete = 0;
    var salearn  = 0;
    var use_alt  = 0;
    e.preventDefault();
    if(dojo.byId("id_release").checked){
        release = 1;
    }
    if(dojo.byId("id_todelete").checked){
        todelete = 1;
    }
    if(dojo.byId("id_salearn").checked){
        salearn = 1;
    }
    if(dojo.byId("id_use_alt").checked){
        use_alt = 1;
    }
    dojo.xhrPost({
        url: '/messages/process_quarantine/',
        handleAs: "json",
        content: {
             release:        release,
             todelete:       todelete,
             salearn:        salearn,
             salearn_as:     dojo.byId("id_salearn_as").value,
             use_alt:        use_alt,
             altrecipients:  dojo.byId("id_altrecipients").value,
             message_id:     dojo.byId("id_message_id").value
        },
        handle: function(data,args){
            dojo.byId("ajax_status").innerHTML = "";
            if(typeof data == "error"){
                dojo.byId("quarantine_errors").innerHTML = args;
                dojo.attr("submit_q_request","disabled",false);
            }else{
                dojo.byId("quarantine_errors").innerHTML = "";
                dojo.byId("server_response").innerHTML = "";
                if(data.success == "True"){
                    dojo.byId("server_response").innerHTML = data.html;
                    dojo.destroy("process_quarantine");
                    dojo.destroy("ajax_status");
                    dojo.destroy("quarantine_errors");
                }else{
                    dojo.byId("quarantine_errors").innerHTML = data.html;
                    dojo.attr("submit_q_request","disabled",false);
                }
            }
        }
    });
}

dojo.addOnLoad(function(){
    dojo.byId("mail-headers").style.display = "none";
    dojo.create("a",{href:"#",innerHTML:"&darr;&nbsp;Show headers",id:"header-toggle"},"mail-headers","after");
    var process_form = dojo.byId("qform");
    dojo.connect(process_form,"onsubmit","formSubmission"); 
    //dojo.connect(dojo.byId("whitelist"),"onclick","handleListing");
    //dojo.connect(dojo.byId("blacklist"),"onclick","handleListing");
    node = dojo.query("whitelist");
    if(node){node.onclick(handleListing);}
    node = dojo.query("blacklist");
    if(node){node.onclick(handleListing);}
    dojo.connect(dojo.byId("header-toggle"),"onclick",function(e){
        e.preventDefault();
        em = dojo.byId("mail-headers");
        if(em.style.display == "block"){
            em.style.display = "none";
            dojo.byId("header-toggle").innerHTML = "&darr;&nbsp;Show headers";
        }else{
            em.style.display = "block";
            dojo.byId("header-toggle").innerHTML = "&uarr;&nbsp;Hide headers";
        }
    });
});
