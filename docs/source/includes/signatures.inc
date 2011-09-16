**Configure Email Signature management**

Baruwa now supports the management of email signatures / disclaimers
from within the web interface. Signatures are configured on a domain
and user level.

Both HTML and text signatures are supported, HTML signatures support
embedding of one graphical image, which can be uploaded via the HTML
editor interface.

The backend that handles the signatures needs to be initialized before
you can begin to manage the signatures via the interface.

To initialize the backend run::

   # baruwa-admin initconfig

This will ask you for the hostname of the system you are setting up,
and then initialize the system for you. The command does attempt to
guess your hostname, so if its correct just press enter.

You need to initialize each of your machines if you are running a
clustered setup.

