**Configure celeryd to run as a daemon**

You need to run celeryd as a daemon in order to process tasks such as
Bayesian learning and message releases from the quarantine etc etc.

An init script /etc/init.d/baruwa and configuration file /etc/sysconfig/baruwa
are installed by the Baruwa rpm all you need to do is enable celeryd to be
started at system boot by running::

	# chkconfig --level 35 baruwa on
	# service baruwa start
