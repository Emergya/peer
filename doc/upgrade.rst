Upgrade process
===============

Upgrading your PEER software is an easy task and your data will be safe. You
just need to follow these steps. If you installed PEER with docker, you should
got to the documentation for
`peer-dockerfiles <https://github.com/Emergya/peer-dockerfiles>`_.

Upgrading the PEER package
--------------------------

If you followed the :doc:`install` instructions you should have a virtualenv
where everything related to PEER is isolated. So, let's activate that
virtualenv to avoid messing the system:

.. code-block:: bash

  $ source /vaw/www/peer/bin/activate

now we can just upgrade the PEER package:

.. code-block:: bash

  $ easy_install --upgrade peer

If there is a newer version of PEER, easy_install will download and install
it in the lib/python2.7/site-packages directory of your virtualenv. This will
not overwrite your old peer version, which is convenient since we will need
to copy the *local_settings.py* file from that old directory.

Copying your old local_settings.py file
---------------------------------------

The local_settings.py is where your custom configuration settings should
have been placed as explained in the :doc:`configuration` section. Now just
copy that file into the new peer directory:

.. code-block:: bash

  $ cp /var/www/peer/lib/python2.7/site-packages/peer-0.4.0-py2.7.egg/peer/local_settings.py /var/www/peer/lib/python2.7/site-packages/peer-0.5.0-py2.7.egg/peer/

In this example we are upgrading from version 0.4.0 to version 0.5.0. Adjust
your paths according to your case.

Updating your database schema
-----------------------------

Sometimes, between PEER versions, the database schema changes and need to be
updated. After each upgrade it is a good moment to do so and the following
command should be executed.

.. code-block:: bash

  $ source /vaw/www/peer/bin/activate
  $ django-admin.py migrate --settings=peer.settings

It is safe to execute this command any time, even if there are no changes
in the database schema.

Updating your static files
--------------------------

If the new version you are upgrading too has new static files or has changed
any of the old static files you should copy them again to their final
destination:

.. code-block:: bash

  $ source /vaw/www/peer/bin/activate
  $ django-admin.py collectstatic --settings=peer.settings

It is safe to execute this command any time, even if there are no changes
in the static files. It will only copy those files that are needed.

Adjusting your web server configuration
---------------------------------------

The last thing you need to do in the upgrade process is to adjust the
absolute paths to the PEER wsgi script and static directory in your
web server configuration.

For example, if you had this configuration in Apache:

.. code-block:: none

 WSGIScriptAlias / /vaw/www/peer/lib/python2.7/site-packages/peer-0.4.0-py2.7.egg/peer/peer.wsgi
 Alias /static/ /vaw/www/peer/lib/python2.7/site-packages/peer-0.4.0-py2.7.egg/peer/static/

And you are upgrading to version 0.5.0, you need to change it to this:

.. code-block:: none

 WSGIScriptAlias / /vaw/www/peer/lib/python2.7/site-packages/peer-0.5.0-py2.7.egg/peer/peer.wsgi
 Alias /static/ /vaw/www/peer/lib/python2.7/site-packages/peer-0.5.0-py2.7.egg/peer/static/
