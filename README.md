

Baruwa
==
Baruwa (swahili for letter or mail) is a web 2.0 [MailScanner](http://www.mailscanner.info/ "")
front-end. 

It provides an easy to use interface for managing a MailScanner installation. It is used to
perform operations such as releasing quarantined messages, spam learning, whitelisting and 
blacklisting addresses, monitoring the health of the services etc. Baruwa is implemented 
using web 2.0 features (AJAX) where deemed fit, graphing is also implemented on the client
side using SVG, Silverlight or VML. Baruwa has full support for i18n, letting you support 
any language of your choosing.

It includes reporting functionality with an easy to use query builder, results can be 
displayed as message lists or graphed as colorful and pretty interactive graphs.

Custom MailScanner modules are provided to allow for logging of messages to the mysql
database with SQLite as backup, managing whitelists and blacklists and managing per
user spam check settings.

Baruwa is open source software, written in Python/Perl using the Django Framework and 
MySQL for storage, it is released under the GPLv2 and is available for free download.


Features
==
+ AJAX support for most operations
+ Reporting with AJAX enabled query builder
+ I18n support, allows use of multiple languages
+ Interactive SVG graphs and PDF reports
+ Archiving of old message logs
+ SQLite backup prevents data loss when MySQL is down
+ MTA integration for relay domains and transports configuration
+ Multi user profiles (No restrictions on username format)
+ User profile aware white/blacklist management
+ Ip / network addresses supported in white/blacklist manager
+ Easy plug-in authentication to external authentication systems (POP3, IMAP and SMTP supported out of the box)
+ Tools for housekeeping tasks (quarantine management, rule updates, quarantine notifications, etc)
+ Works both with and without Javascript enabled (graphs require Javascript)


Screenshots
==
[Screenshots](http://www.flickr.com/photos/baruwa/ "Screenshots") are on our Flickr page.


Requirements
==
+ Python >= 2.4
+ Django >= 1.1.1
+ MySQLdb >= 1.2.1p2
+ GeoIP
+ iPy
+ Any Web server that can run Django (Apache/mod_wsgi recommended)
+ MySQL
+ Dojo toolkit
+ Reportlab
+ Lxml
+ UUID (python 2.4 only)
+ Sphinx (optional for building docs)

Note
==
Baruwa 1.0.x is not compatible with the 0.0.x versions and Mailwatch, as it
uses a different database schema and its own MailScanner custom modules.


Installation
==
Baruwa is installed in the usual way

    python setup.py install


Packages
==
Binary packages for [Ubuntu/Debian, Fedora and RHEL/CENTOS](http://topdog-software.com/oss/baruwa/ "") 
are available for download.


Documentation
==
Documentation is included in the docs directory of the tar ball and can also be accessed 
[online](http://www.baruwa.org/)


Support
==
Subscribe to the [Baruwa mailing list](http://lists.baruwa.org/mailman/listinfo/baruwa)

