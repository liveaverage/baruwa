Configure RabbitMQ
==================

Create a user and virtual host for baruwa::

    # rabbitmqctl add_user baruwa your_password
    # rabbitmqctl add_vhost baruwa
    # rabbitmqctl set_permissions -p baruwa baruwa ".*" ".*" ".*"

Delete the guest user::

	# rabbitmqctl delete_user guest

See the RabbitMQ `Admin Guide`_ for more information.

.. note::

	Please ensure that you control access to your RabbitMQ install
	as to prevent an unauthorized clients from accessing your broker.

.. _`Admin Guide`: http://www.rabbitmq.com/admin-guide.html