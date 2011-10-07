

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
MySQL or PostgreSQL for storage, it is released under the GPLv2 and is available for
free download.


Features
==
+ AJAX support for most operations
+ Reporting with AJAX enabled query builder
+ I18n support, allows use of multiple languages
+ Signature management / Branding
+ Mail queue management and reporting
+ Interactive SVG graphs
+ Emailed PDF reports
+ Archiving of old message logs
+ SQLite backup prevents data loss when MySQL or PostgreSQL is down
+ MTA integration for relay domains and transports configuration
+ Multi user profiles (No restrictions on username format)
+ User profile aware white/blacklist management
+ Ip / network addresses supported in white/blacklist manager
+ Easy plug-in authentication to external authentication systems (POP3, IMAP, SMTP and RADIUS supported out of the box)
+ Tools for housekeeping tasks (quarantine management, rule updates, quarantine notifications, etc)
+ Easy clustering of multiple servers
+ Works both with and without Javascript enabled (graphs require Javascript)


Screenshots
==
[Screenshots](http://www.baruwa.org/about/screenshots.html "Screenshots") are on our site.


Requirements
==
+ Python >= 2.4
+ Django >= 1.2
+ django-celery
+ MySQLdb >= 1.2.1p2 or Psycopg
+ GeoIP
+ iPy
+ Any Web server that can run Django (Apache/mod_wsgi recommended)
+ MySQL or PostgreSQL
+ Dojo toolkit >= 1.5.0
+ Reportlab
+ Lxml
+ Anyjson
+ A message broker (RabbitMQ recommended)
+ UUID (python 2.4 only)
+ Sphinx (Optional for building docs)
+ Pyrad (Optional for RADIUS/RSA SECURID authentication)

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
Binary packages for Ubuntu/Debian, Fedora and RHEL/SL/CENTOS are available.

+ [RHEL/SL/CENTOS](http://repo.baruwa.org)
+ [Ubuntu/Debian](http://apt.baruwa.org)


Documentation
==
Documentation is included in the docs directory of the tar ball and can also be accessed 
[online](http://www.baruwa.org/documentation/)


Support
==
Subscribe to the [Baruwa mailing list](http://lists.baruwa.org/mailman/listinfo/baruwa)

