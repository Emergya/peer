Installation
============

In this part two types of installation will be covered: the standard one
aimed for production and the development one, which target audience is
the developer community. An alternative method, using docker, is described
`here <https://github.com/Emergya/peer-dockerfiles>`_.

After these steps you should have a PEER instance up and running but
please note that many configuration defaults will not be good for your
installation. It is recommended to read the :doc:`configuration` chapter
right after this one.

Common prerequisites
--------------------

The version of Python needed to run PEER is 2.7.

In the process of installing PEER, both in the standard installation and
the development installation, it is necessary that some libraries already
exist on your system. It is also needed the basic compiler chaintool and
the development version of those libraries since the installation process
compiles a couple of Python modules.

.. code-block:: bash

  # Fedora example:
  $ yum install python-devel libxml2-devel libxml2 libxslt-devel libxslt xmlsec1 xmlsec1-openssl postgresql-devel
  $ yum groupinstall "Development Tools"

  # Debian/Ubuntu example:
  $ apt-get install build-essential python-dev libxml2-dev libxml2 libxslt1-dev libxslt1.1 xmlsec1 libxmlsec1-openssl libpq-dev swig

Standard installation
---------------------

The standard installation is recommended for having a glimpse at the PEER
application and also for real production deployment.

Creating a virtualenv
~~~~~~~~~~~~~~~~~~~~~

When installing a python application from the source you may put it in your
system python site-packages directory running the standard
*python setup.py install* dance but that is not recommended since it will
pollute your system Python and make upgrades unnecessarily difficult. If
the python application have some dependencies, as the PEER application has,
things will become worse since you may have conflicts between the
dependencies versions needed by the application and the versions installed
on your system and needed by other applications.

.. note::
  You should always install software using your Linux distribution packages.
  Python applications are not a exception to this rule. This documentation
  assumes that there is no PEER package yet in your Linux distribution or
  it is very out of date.

For all these reasons it is highly recommended to install the PEER
application (any as a general rule, any Python application) in its own
isolated environment. To do so there are a number of tools available. We
will use *virtualenv* in this section and *buildout* in the Development
installation section.

So first we will install virtualenv:

.. code-block:: bash

  # Fedora example:
  $ yum install python-virtualenv

  # Debian/Ubuntu example:
  $ apt-get install python-virtualenv

Check your distribution documentation if you do not use neither Fedora nor
Ubuntu.

Now a new command called *virtualenv* is available on your system and we
will use it to create a new virtual environment where we will install PEER.

.. code-block:: bash

  $ virtualenv /var/www/peer --no-site-packages

The *--no-site-packages* option tells virtualenv to not depend on any system
package. For example, even if you already have Django installed on your
system it will install another copy inside this virtualenv. This improves
the reliability by making sure you have the same versions of the
dependencies that the developers have tested.

.. note::
  We are using the system python and not a custom compiled one, which would
  improve the system isolation, because we are going to deploy the
  application with Apache and mod_wsgi and they depend on the system python.


Installing PEER and its dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this step the PEER software and all its depenencies will get installed
into the virtualenv that was just created in the previous step.

We first need to activate the virtualenv:

.. code-block:: bash

  $ source /var/www/peer/bin/activate

This will change the *PATH* and some other environment variables so this
will take precedence over your regular system python.

Now we can install the PEER software:

.. code-block:: bash

  $ easy_install peer

After a while you will have a bunch of new packages inside
*/var/www/peer/lib/python2.7/site-packages/*

Creating the database
~~~~~~~~~~~~~~~~~~~~~

The PEER application uses two types of storage:

- A VCS system to store entities metadata. Right now only Git is supported
  but the interface is abstract enough to support other backends.
- A relational database to store domains, users and other information
  besides the entities themselves.

PEER creates the repository where it stores the entities metadata
automatically so you do not need to setup anything. However the relational
database needs to be created and configured manually.

Being a Django project, the PEER application support several different types
of SQL databases such as Postgresql, Mysql, Sqlite, Oracle, etc.

In this documentation we will cover the installation with a Postgresql
database because it is the RDMS we recommend. Check the
`Django documentation`_ to learn how to configure other database backends.

.. _`Django documentation`: http://docs.djangoproject.com/

The first step is to install database server. It is recommended to use the
packages for your Linux distribution:

.. code-block:: bash

  # Fedora example:
  $ yum install postgresql postgresql-server postgresql-libs

  # Debian/Ubuntu example:
  $ apt-get install postgresql postgresql-client

Check your distribution documentation if you do not use neither Fedora nor
Ubuntu.

Now a database user and the database itself must be created. The easiest way
to do this is to login as the postgres system user and creating the user
with that account:

.. code-block:: bash

  $ su - postgres
  $ createuser peer --no-createrole --no-createdb --no-superuser -P
  Enter password for new role: *****
  Enter it again: *****
  $ createdb -E UTF8 --owner=peer peer

With the previous commands we have created a database called *peer* and a
user, which owns the database, called also *peer*. When creating the user
the createuser command ask for a password. You should remember this password
in a later stage of the installation/configuration process.

Now we need to configure Postgresql to accept database connections from the
*peer* user into the *peer* database. To do so, we need to add the following
directive in the pg_hba.conf file:

.. code-block:: bash

  # TYPE   DATABASE    USER       CIDR-ADDRESS        METHOD
  local    peer        peer                           md5

And restart the Postgresql server to reload its configuration:

.. code-block:: bash

  $ service postgresql restart

.. note::
  The location of the pg_hba.conf file depends on your Linux distribution. On
  Fedora it is located at /var/lib/pgsql/data/pg_hba.conf but in Ubuntu it is
  located at /etc/postgresql/8.1/main/pg_hba.conf being 8.1 the version of
  Postgresql you have installed.

To check that everything is correct you should try to connect to the *peer*
database using the *peer* user and the password you assigned to it:

.. code-block:: bash

  $ psql -U peer -W peer
  Password for user peer:
  psql (9.0.4)
  Type "help" for help.

  peer=#

.. note::
  We have deliberately kept this postgresql installation super simple since
  we want to focus in the PEER software. If you are serious about puting
  this into production you may consider checking other Postgresql
  configuration settings to improve its performance and security.

Creating the database schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we have to create the database tables needed by PEER but before we need
to configure it to tell the database parameters needed to connect to the
database. This will be described with more deails in the :doc:`configuration`
chapter.

Add the following information into the
*/var/www/peer/lib/python2.7/site-packages/peer-X.Y.Z-py2.7.egg/peer/local_settings.py* file:

.. code-block:: python

 DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': 'peer',
         'USER': 'peer',
         'PASSWORD': 'secret',
         'HOST': '',
         'PORT': '',
     }
 }

Fill this dictionary with the appropiate values for your database
installation, as performed in the previous step.

.. note::
  The location of the *local_settings.py* file depends on the PEER version
  that you have. The path fragment :file:`peer-X.Y.Z-py2.6` is ficticious and will
  be something like |full_release_name| in real life.

Then, activate the virtualenv:

.. code-block:: bash

  $ source /var/www/peer/bin/activate

And run the Django migrate command to create the database schema:

.. code-block:: bash

  $ django-admin.py migrate --settings=peer.settings

Creating a superuser
~~~~~~~~~~~~~~~~~~~~

After this, it is necessary to create a superuser named 'admin'. This
administrator's name should be `admin` because there are fixtures that
depends on this name. You can create more administrators in the future
with other names.

.. code-block:: bash

  $ django-admin.py createsuperuser --settings=peer.settings --username=admin --email=admin@example.com

Write this admin's username and password down. You will need them later.

Collecting static files
~~~~~~~~~~~~~~~~~~~~~~~

In this step you will collect all necessary static resources needed by
PEER and put them in a single directory so you can serve them directly
through your web server increasing the efficiency of the whole system.

The nice thing is that you don't have to do this manually. There is a
Django command just for that:

.. code-block:: bash

  $ django-admin.py collectstatic --settings=peer.settings

 You have requested to collect static files at the destination
 location as specified in your settings file.

 This will overwrite existing files.
 Are you sure you want to do this?

 Type 'yes' to continue, or 'no' to cancel: yes


Configuring the web server
~~~~~~~~~~~~~~~~~~~~~~~~~~

The recommended way to serve a PEER site is with a real web server that
supports the WSGI (Web Server Gateway Interface) protocol. This is no
surprise since the same applies to Django.

If you use the Apache web server all you need to do is write the
following configuration into your specific virtual host section:

.. code-block:: none

 WSGIScriptAlias / /var/www/peer/lib/python2.7/site-packages/peer-X.Y.Z-py2.7.egg/peer/peer.wsgi
 Alias /static/ /var/www/peer/lib/python2.7/site-packages/peer-X.Y.Z-py2.7.egg/peer/static/


.. note::
  Bear in mind that the exact path may be different in your case, specially
  the Python and PEER version numbers. The path
  fragment :file:`peer-X.Y.Z-py2.7` is ficticious and will be something like
  |full_release_name| in real life.


The packages needed for installing Apache and wsgi support are:

.. code-block:: bash

  # Fedora example:
  $ yum install httpd mod_wsgi

  # Debian/Ubuntu example:
  $ apt-get install apache2 libapache2-mod-wsgi

.. note::
  If you use someting different from Apache, please check the documentation
  of your web server about how to integrate it with a WSGI application.

Finally, you need to make sure that the user that the Apache run as has write
access to the MEDIA directory of your PEER site. That directory is where
the Git repository for the entities' metadata is created and maintained.

.. code-block:: bash

  # Fedora example:
  $ chown apache:apache /var/www/peer/lib/python2.7/site-packages/peer-X.Y.Z-py2.7.egg/peer/media

  # Debian/Ubuntu example:
  $ chown www-data:www-data /var/www/peer/lib/python2.7/site-packages/peer-X.Y.Z-py2.7.egg/peer/media

.. note::
  As mentioned before, the exact path may be different in your case, specially
  the Python and PEER version numbers. The path
  fragment :file:`peer-X.Y.Z-py2.7` is ficticious and will be something like
  |full_release_name| in real life.


Development installation
------------------------

You can start by cloning the PEER repository, substituting <username> with
your Github username:

.. code-block:: bash

  $ git clone https://<username>@github.com/Emergya/peer.git

As in the standard installation we will create a virtualenv to isolate the
system from the packages that the installation process is going to add.

You can read more about this in the `Creating a virtualenv`_ section. Just
install virtualenv if you haven't already done it:

.. code-block:: bash

  # Fedora example:
  $ yum install python-virtualenv

  # Debian/Ubuntu example:
  $ apt-get install python-virtualenv

And create the virtualenv in the same directory where you cloned the PEER
repository:

.. code-block:: bash

  $ cd peer
  $ virtualenv . --no-site-packages
  $ source bin/activate   # don't forget to activate the virtualenv

Now we will create a buildout using the bootstrap script.

.. code-block:: bash

  $ python bootstrap.py
  $ bin/buildout

.. note::
  Buildout is a Python package which purpose is to collect all the
  dependencies and configuration needed to run a software. It is not
  specific to Python software but obviously it is a good fit in those
  cases.

The bin/buildout command will take a while so you can create your database
in the meantime. Check the `Creating the database`_ section of the standard
installation to learn how to do it. By default the PEER software is expecting
the database to be called `peer` and a user called `peer` to access that
database with a password equal to `peer`. But of course you can configure
PEER to use anything else.

As soon as you have the database created and the buildout command has
finished you can populate the database to create the schema:

.. code-block:: bash

   $ bin/django migrate

Create a supersuser:

.. code-block:: bash

   $ bin/django createsuperuser --username=admin --email=admin@example.com

And now you are ready to run the embedded Django server, which is perfectly
fine for development purposes.:

.. code-block:: bash

   $ bin/django runserver

.. note::
  All traditional django-admin.py commands or manage.py commands are
  available in the builoudt as bin/django commands.


It is also recommended that you activate DEBUG mode in your configuration
file. We will see how to do that in the next chapter, :doc:`configuration`.
