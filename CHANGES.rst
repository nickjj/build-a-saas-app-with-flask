Version 1.1.1 (2015-10-29)
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Fix the Stripe API version so that customer.card exists
- Fix inaccurate created/updated at timestamps on all resources
- Update the favicon

Version 1.1.0 (2015-08-25)
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Add a new ``run db init`` command to quickly initialize a new database
- Set ``NODE_ENV`` to ``production`` when building assets

Version 1.0.0 (2015-08-17)
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Remove the ``migrate`` command in favor of using Alembic directly
- Fix ``PUBLIC_PATH`` in the ``Dockerfile``
- Add a way to contact issue openers through the admin
- Fix aborting bulk delete if 1 resource is invalid
- Add passive deletes to invoices
- Fix live stream menu from showing when unsubscribed
- Add new decorator ``subscription_required``
- Fix unsubscribed users from being able to see the Twitter stream
- Fix null template error for tax/tax_percent calculations
- Fix coupons to ensure they are always capitalized when created
- Remove unused timezone from initializer
- Fix users from being able to change their username
- Add new CLI command ``run secret`` to generate a random token
- Reorganize production settings

Version 0.2.0 (2015-07-04)
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Fix IP address logging by using request.remote_addr
- Fix exception when g.start could not exist
- Update psycopg2, Flask-Webpack and pytest dependencies
- Fix missing payment errors alert in credit card form
- Fix legacy print call in the CLI module
- Replace the rome datetime picker with a Bootstrap 3 dt picker
- Fix Coupon redeem_by not being timezone aware
- Add web UI component for monitoring Celery tasks
- Fix the seeded admin account so it's always set to an English locale
- Add Dockerfile
- Add web UI component for system health monitoring

Version 0.1.0 (2015-06-24)
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Add i18n support along with a Spanish translation
- Use timezone aware UTC dates on the Python side
- Use momentjs to handle all date formatting
- Update forms to process all HTTP verbs
- Add new functionality to the ``run db`` commands
- Fix going to the "next" url after login
- Use JSON as a Celery serializer
- Fix missing admin seed account when running ``run add users``
- Add example settings.py file for production use
- Add Google Analytics snippet
- Change the theme to Bootstrap
- Drastically enhance the webpack set up
- Add custom error pages
- Add robots.txt and public favicons
- Fix not cancelling subscriptions when deleting users
- Major refactor of the entire code base
- Adapt MIT license to the code base
- Upgrade multiple package dependencies
- Upgrade Postgres and Redis versions

Version 0.0.2 (2015-06-05)
^^^^^^^^^^^^^^^^^^^^^^^^^^

- 80%+ test coverage
- Real time cat stream from Twitter
- Custom websocket server to broadcast the tweets
- End to end recurring billing solution
- Full blown CLI tool to manage your project
- Home grown admin panel

Version 0.0.1 (2015-05-20)
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Initial release
