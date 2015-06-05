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
own for setting up virtualenv, installing Docker, installing nodejs and doing
the post-install steps.

Install Virtualenv
''''''''''''''''''

- https://virtualenv.pypa.io/en/latest/installation.html

Install Docker
''''''''''''''

- https://docs.docker.com/installation (docker itself)
- https://github.com/docker/compose/releases (docker-compose tool for development)

Install nodejs
''''''''''''''

- https://nodejs.org/download/ (runtime dependency for assets)

Register on Stripe to get your API keys
'''''''''''''''''''''''''''''''''''''''

- https://dashboard.stripe.com/register
- Go to your account settings on Stripe
- Copy your API keys
- Follow the directions in ``config/settings.py``

Review the plans in the above settings file before proceeding. You can always
change or delete plans later, so don't sweat it. Just make sure you know
what's being created.

I installed everything, now what?
'''''''''''''''''''''''''''''''''

Create a bit of supporting directory structure
----------------------------------------------

- Create a new folder somewhere, let's say: ``/tmp/testsaasapp``
- Create a new ``website`` folder inside of that: ``/tmp/testsaasapp/website``
- CD into that directory: ``cd /tmp/testsaasapp/website``

Clone the repo and install all dependencies
-------------------------------------------

- Clone this repo ``git clone https://github.com/nickjj/build-a-saas-app-with-flask``
- Type ``cd build-a-saas-app-with-flask``
- Activate your virtualenv
- Type ``pip install --editable .`` to activate the CLI
- Type ``pip install -r requirements.txt`` to install dependencies
- Type ``npm install`` to install the asset dependencies

Set up docker-compose
---------------------

- Edit ``docker-compose.yml`` and `setup a local volume for Postgres/Redis`__
- Type ``docker-compose up`` to start Postgres/Redis

Initialize everything and view the app
--------------------------------------

- Open a new terminal window
- Type ``run`` to see a list of what's available
- Type ``run assets build`` to create the build directory
- Type ``run db reset`` to initialize the database
- Type ``run stripe sync_plans`` to sync your ``STRIPE_PLANS`` to Stripe
- Type ``run all`` to start everything
- Visit http://localhost:8000 in your browser
- If you wish to login, email: ``dev@localhost.com`` / password: ``password``

Do I need to do the above steps all the time?
'''''''''''''''''''''''''''''''''''''''''''''

Heck no, from now on you only need to do this:

- Activate your virtualenv
- Type ``run all`` to start everything
- Visit http://localhost:8000 in your browser

Also in the future I will be working on ways to automate the above steps. You
have to remember the above steps are replacing things like Vagrant and more.

You just setup a complete dev environment which you can reproduce on
any machine capable of running Docker. Your environment is now very close to
what we will be running in production.

How do I shut everything down?
''''''''''''''''''''''''''''''

- Hit CTRL+C a few times to stop everything
- Type ``docker-compose stop`` to ensure all containers are stopped
- Confirm no containers are running by typing ``docker ps``

How do I provide my own settings?
'''''''''''''''''''''''''''''''''

- Create an ``instance/`` folder in the root of the project
- Create a ``settings.py`` file at ``$PROJECT_ROOT/instance/settings.py``
- Overwrite as many settings as you want

For example, your ``instance/settings.py`` file might end up looking like:

::

    STRIPE_SECRET_KEY = 'realkeygoeshere'
    STRIPE_PUBLISHABLE_KEY = 'thisonetoo'

    MAIL_USERNAME = 'yourrealaccount@gmail.com'
    MAIL_PASSWORD = 'seriousbusinesspassword'

Can I quickly change my schema without migrating?
'''''''''''''''''''''''''''''''''''''''''''''''''

Yep, just be warned that this will completely purge your database but doing
this early on in development can sometimes be reasonable while you tinker with
your schema very frequently.

- Shut everything down
- Type ``docker-compose run postgres``
- Type ``run db reset catwatch catwatch_test``
- Type ``run add all``

This will drop your database, create a new one and seed it with fake data.

My billing history is always empty
''''''''''''''''''''''''''''''''''

Filling out the billing history requires setting up webhooks with Stripe. You
can do that in your Stripe account dashboard under webhooks.

You will need to setup something like ngrok so localhost is accessible outside
of your local network. It does this by setting up a tunnel.

Also make sure to look at the comments in ``config/settings.py`` for the
``SERVER_NAME`` setting.

How can I test the Twitter stream?
''''''''''''''''''''''''''''''''''

After everything is running and your settings are configured just type ``run stream broadcast``
and it will start reading in events from Twitter and broadcast the messages to the
websocket server.

You can bypass broadcasting and simply listen it on the stream by typing
``run stream listen`` instead.

Learn more
^^^^^^^^^^

What packages are being used?
'''''''''''''''''''''''''''''

Check the commented ``requirements.txt`` for package specifics.

How will the project be managed?
''''''''''''''''''''''''''''''''

Upcoming features
-----------------

I'm an organized person but not OCD about it. I will do my best to add pending
features to the issue tracker with a specific label. Not all features will get
added to the issue tracker because who wants to write issues all day!

Branches
--------

The latest "unstable but might be stable" version will be master.

Stable releases will be tagged and released using the http://semver.org/ system.
However early on in the project there's a very good chance the versions will
not adhere to semver perfectly.

__ https://github.com/nickjj/build-a-saas-app-with-flask/commit/9031114d3f0880e01a9f97df9f924dbb1238a092

.. |Build status| image:: https://secure.travis-ci.org/nickjj/build-a-saas-app-with-flask.png
   :target: https://travis-ci.org/nickjj/build-a-saas-app-with-flask

.. |Flattr this git repo| image:: http://api.flattr.com/button/flattr-badge-large.png
   :target: https://flattr.com/submit/auto?user_id=nickjj&url=https://github.com/nickjj/build-a-saas-app-with-flask&title=Build+a+SAAS+app+with+Flask&language=Python&tags=github&category=software
