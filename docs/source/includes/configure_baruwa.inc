Configure Baruwa
================

**Create the database**::

    # mysqladmin -u root -p create baruwa

**Create a Mysql user for baruwa**

Run the command from the mysql prompt::

    mysql> GRANT ALL ON baruwa.* TO baruwa@localhost IDENTIFIED BY '<password>';
    mysql> flush privileges;

.. note::

	You may want to secure your system by creating several users will limited rights
	as opposed to the above where the user has full access to the DB.

**Configure the Baruwa settings**

Edit the Baruwa settings.py file::

	# baruwa_path=$(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")
	# vi $baruwa_path/baruwa/settings.py
	
Set the following options::

    DATABASE_NAME = 'baruwa'
    DATABASE_USER = 'baruwa'
    DATABASE_PASSWORD = '<password>'
    DATABASE_HOST = 'localhost'

Populate the database and create admin user::

	# baruwa-admin syncdb
	
The syncdb command populates your SQL database and allows you 
to create the admin user.

Set the rabbitMQ settings::

	CELERY_CONCURRENCY = 20
	BROKER_HOST = "localhost"
	BROKER_PORT = 5672
	BROKER_USER = "baruwa"
	BROKER_PASSWORD = "your_password"
	BROKER_VHOST = "baruwa"

Edit the settings.py file and make configuration changes to suit your site.::

	# vi $baruwa_path/baruwa/settings.py

.. warning::
    
    Make sure you change the SECRET_KEY, DO NOT USE THE DEFAULT, If you have a cluster the key
    should be the same on all the machines in the cluster.