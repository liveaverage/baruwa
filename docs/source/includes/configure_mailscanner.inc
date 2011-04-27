Configure MailScanner
=====================

It is assumed that you have a working MailScanner system already installed
and configured, if you are installing from scratch please refer to their
documentation on how to install and configure MailScanner.

**Install the Baruwa MailScanner Custom modules**

Copy them to the MailScanner custom functions directory::

	# confdir=$(/usr/sbin/Quick.Peek 'Custom Functions Dir' /etc/MailScanner/MailScanner.conf)
	# cp extras/{BaruwaSQL.pm, BaruwaLists.pm, BaruwaUserSettings.pm} $confdir/

.. note::

	Starting with Baruwa version 1.1.0 you no longer have to edit and set the
	DB authentication details in each and every Custom module, you just set them
	up once in the MailScanner configuration file, A sample configuration file is
	provided you simply customize that and drop it into the configuration directory
	and it will override the settings in your MailScanner.conf file.

Edit the provided MailScanner config file extras/baruwa-mailscanner.conf,
you need to make sure the following options are correct::

    Quarantine User = exim #(Or what ever your "Run As User" is set to)
    DB DSN = DBI:mysql:database=baruwa;host=spam01;port=3306 #set to valid DSN
    DB Username = baruwa # your DB username
    DB Password = password # your DB password

To actually quarantine and later process messages with in Baruwa, set
'store' as one of your keywords for the "Spam Actions" and
"High Scoring Spam Actions" MailScanner options.

The provided MailScanner configuration provides for SQL logging, Whitelists and
Blacklists and Per user settings. Copy the file into the MailScanner configuration
directory::

	# cp extras/baruwa-mailscanner.conf /etc/MailScanner/conf.d/baruwa.conf
	
In some cases your MailScanner configuration directory is under /opt::

	# cp extras/baruwa-mailscanner.conf /opt/etc/MailScanner/conf.d/baruwa.conf

**Apply configuration changes**

Test your configuration for any errors::

	# MailScanner --lint

Restart MailScanner::

    # /etc/init.d/MailScanner restart