Testing
=======

**Verify that is working**

Check your log files you should see

Baruwa SQL logger::

	Aug  9 18:58:27 localhost MailScanner[8470]: Logging message 1OiVg7-0003zS-9s to Baruwa SQL 
	Aug  9 18:58:27 localhost MailScanner[11052]: 1OiVg7-0003zS-9s: Logged to Baruwa SQL

Baruwa Lists::

	Aug 9 18:32:42 localhost MailScanner[27260]: Starting Baruwa whitelists 
	Aug 9 18:32:42 localhost MailScanner[27260]: Read 6 whitelist items 
	Aug 9 18:32:42 localhost MailScanner[27260]: Ip blocks whitelisted 192.168.1.0/24 192.168.2.0/24
	xxx.xx.xxx.0/26

Baruwa User settings::

    Aug 9 15:00:03 localhost MailScanner[25708]: Baruwa - Populating spam score settings
    Aug 9 15:00:03 localhost MailScanner[25708]: Read 1 spam score settings
    Aug 9 14:59:53 localhost MailScanner[25668]: Baruwa - Populating high spam score settings
    Aug 9 14:59:53 localhost MailScanner[25668]: Read 1 high spam score settings

Point your browser to http://hostname_used login with admin user and password
and start working. You can now use the interface to add users, domains and 
process messages, etc etc.