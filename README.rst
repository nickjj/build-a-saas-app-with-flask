|Build status|

What is this project?
^^^^^^^^^^^^^^^^^^^^^

This is the source code for the **Build a SAAS app with Flask** project. It is
currently on Kickstarter. Join me in making an awesome community resource:

https://www.kickstarter.com/projects/nickjj/build-a-saas-app-with-flask-and-deploy-it-with-doc

Want to donate but can't use Kickstarter?
'''''''''''''''''''''''''''''''''''''''''

|Flattr this git repo|

Installation instructions
^^^^^^^^^^^^^^^^^^^^^^^^^

This process will be more streamlined in the future but for now you're on your
own for setting up virtualenv and installing Docker.

Install Virtualenv
''''''''''''''''''

- https://virtualenv.pypa.io/en/latest/installation.html

Install Docker
''''''''''''''

- https://docs.docker.com/installation (docker itself)
- https://github.com/docker/compose/releases (docker-compose tool for development)

I installed everything, now what?
'''''''''''''''''''''''''''''''''

- Clone this repo ``git clone https://github.com/nick/build-a-saas-app-with-flask.git``
- Type ``cd build-a-saas-app-with-flask``
- Activate your virtualenv
- Type ``pip install --editable .`` to activate the CLI
- Type ``pip install -r requirements.txt`` to install dependencies
- Type ``run`` to see a list of what's available
- Edit ``docker-compose.yml`` and setup a local volume for Postgres/Redis
- Type ``docker-compose up`` to start Postgres/Redis
- Type ``run db reset`` to initialize the database
- Type ``run all`` to start everything
- Visit http://localhost:8000 in your browser
- If you wish to login, email: ``dev@localhost.com``, password: ``password``

What's the workflow after I do the above at least once?
-------------------------------------------------------

- Activate your virtualenv
- Type ``run all`` to start everything
- Visit http://localhost:8000 in your browser

How do I shut everything down?
------------------------------

- Hit CTRL+C a few times to stop everything
- Type ``docker-compose stop`` to ensure all containers are stopped

How do I provide my own settings?
---------------------------------

- Create an ``instance/`` folder in the root of the project
- Create a ``settings.py`` file at ``$PROJECT_ROOT/instance/settings.py``
- Overwrite as many settings as you want

For example, your ``settings.py`` file might end up looking like:

::

    MAIL_USERNAME = 'yourrealaccount@gmail.com'
    MAIL_PASSWORD = 'seriousbusinesspassword'

High level overview
^^^^^^^^^^^^^^^^^^^

What packages are being used?
'''''''''''''''''''''''''''''

Check the commented ``requirements.txt`` for package specifics.

How will the project be managed?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Upcoming features
'''''''''''''''''

I'm an organized person but not OCD about it. I will do my best to add pending
features to the issue tracker with a specific label. Not all features will get
added to the issue tracker because who wants to write issues all day!

Branches
''''''''

The latest "unstable but might be stable" version will be master.

Stable releases will be tagged and released using the http://semver.org/ system.
However early on in the project there's a very good chance the versions will
not adhere to semver perfectly.

.. |Build status| image:: https://secure.travis-ci.org/nickjj/build-a-saas-app-with-flask.png
   :target: https://travis-ci.org/nickjj/build-a-saas-app-with-flask

.. |Flattr this git repo| image:: http://api.flattr.com/button/flattr-badge-large.png
   :target: https://flattr.com/submit/auto?user_id=nickjj&url=https://github.com/nickjj/build-a-saas-app-with-flask&title=Build+a+SAAS+app+with+Flask&language=Python&tags=github&category=software
