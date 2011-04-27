**Setup Web server**

Edit your apache configurations to enable virtual hosting if
not enabled already. Then set the correct hostname in 
/etc/httpd/conf.d/baruwa.conf::

    # change to your hostname
    ServerName baruwa-alpha.local

Make sure mod_wsgi is enabled, uncomment the following line in
/etc/httpd/conf.d/wsgi.conf::

    LoadModule wsgi_module modules/mod_wsgi.so
    
Restart apache.