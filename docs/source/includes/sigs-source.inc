If you are installing from source you need to create the directory
structure to store you signature files::

	# install -p /etc/MailScanner/signatures/{users,domains}/{html,text,imgs}
	# chown celeryd.celeryd -R /etc/MailScanner/signatures/{users,domains}