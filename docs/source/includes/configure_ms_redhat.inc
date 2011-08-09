Configure MailScanner
=====================

It is assumed that you have a working MailScanner system already configured, 
if you are installing from scratch please refer to their documentation on how
to configure MailScanner. The Baruwa repo includes mailscanner and it will be
installed automatically when you install baruwa.

.. note::

	Starting with Baruwa version 1.1.0 you no longer have to edit and set the
	DB authentication details in each and every Custom module, you just set them
	up once in the MailScanner configuration file, A Baruwa MailScanner 
	configuration file is installed as /etc/MailScanner/conf.d/baruwa.conf

Edit the provided Baruwa MailScanner config file /etc/MailScanner/conf.d/baruwa.conf,
you need to make sure the following options are correct::

    Quarantine User = exim #(Or what ever your "Run As User" is set to)
    DB DSN = DBI:mysql:database=baruwa;host=spam01;port=3306 #set to valid DSN
    DB Username = baruwa # your DB username
    DB Password = password # your DB password

To actually quarantine and later process messages with in Baruwa, set
'store' as one of your keywords for the "Spam Actions" and
"High Scoring Spam Actions" MailScanner options.

The provided MailScanner configuration provides for SQL logging, Whitelists and
Blacklists and Per user settings. 

**Apply configuration changes**

Test your configuration for any errors::

	# MailScanner --lint

Restart MailScanner::

    # /etc/init.d/mailscanner restart
