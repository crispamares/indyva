.. _installation:

Installation
============

Indiva depends on several python libraries and `MongoDB
<http://www.mongodb.org/>`_. It is only tested in Linux with Python
2.7, but there are no known restrictions to work on Mac and Windows.

Installing MongoDB
------------------

MongoDB is widely use and should be very easy to install it through
your distribution repositories.

If you use Ubuntu/Debian::

    sudo apt-get install mongodb

The MongoDB version 2.4 is enough, but probably in the future the
requisite will be 2.6 because of improvements in the aggregation
framework. If you prefer the last version, in the `Mongo Documentation
<http://docs.mongodb.org/manual/administration/install-on-linux/>`_
you can find how to install it.

Installing Python Dependencies
------------------------------

There are multiple ways of installing Indiva. Probably the best way of
doing it is using Virtualenv. 

Virtualenv enables multiple installation of Python, one for each
project. It doesn't actually install separate copies of Python, but it
does provide a clever way to keep different project environments
isolated. With virtualenv you will have no conflicts between the
requirements of different projects, you can install different library
versions in your system, even different Python versions.

If you don't have pip install it with::

    sudo apt-get install python-pip

You can install virtualenv in Debian/Ubuntu like this::

    sudo pip install virtualenv

Once you have virtualenv installed, just fire up a shell and create
your own environment. I usually create a project folder, place indyva
folder ins and a create `venv` folder within::

    cd myproject
    virtualenv venv

Now, whenever you want to work on a project, you only have to activate the
corresponding environment. Do the following::

    source venv/bin/activate

You should now be using your virtualenv. Check that the prompt of your
shell has changed to show the active environment.

Now you can install all the dependencies inside your virtualenv::

    pip install gevent
    pip install pymongo
    pip install pyzmq
    pip install pandas
    pip install Werkzeug
    pip install logbook

A few minutes later and you are ready.

The final step is downloading the indiva project (eventually this step
could be completed with pip as well) inside our project directory::

    git clone git@bb13.cesvima.upm.es:jmorales/indyva.git

System-Wide Installation
------------------------

This is possible as well, though I do not recommend it.  Just run
`pip` with root privileges::

    sudo pip install gevent pymongo pyzmq pandas Werkzeug logbook
