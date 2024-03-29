## Welcome to The Build a SAAS App with Flask Course!

*A video course where we build a real world web application with Flask, Celery,
Redis, PostgreSQL, Stripe and Docker.*

**Full details on the course can be found here:**  
[https://buildasaasappwithflask.com](https://buildasaasappwithflask.com/?utm_source=github&utm_medium=bsawf&utm_campaign=readme-top)

### Getting started

You'll need to enable Docker Compose v2 support if you're using Docker
Desktop. On native Linux without Docker Desktop you can [install it as a plugin
to Docker](https://docs.docker.com/compose/install/linux/). It's been generally
available for a while now and is stable. This project uses specific [Docker
Compose v2
features](https://nickjanetakis.com/blog/optional-depends-on-with-docker-compose-v2-20-2)
that only work with Docker Compose v2 2.20.2+.

```sh
cp .env.example .env
docker compose up --build
```

After everything is up and running, visit http://localhost:8000.

Did you receive a `depends_on` "Additional property required is not allowed"
error? Please update to at least Docker Compose v2.20.2+ or Docker Desktop
4.22.0+.

Did you receive an error about a port being in use? Chances are it's because
something on your machine is already running on port 8000. Check out the docs
in the `.env` file for the `DOCKER_WEB_PORT_FORWARD` variable to fix this.

Did you receive a permission denied error? Chances are you're running native
Linux and your `uid:gid` aren't `1000:1000` (you can verify this by running
`id`). Check out the docs in the `.env` file to customize the `UID` and `GID`
variables to fix this.

### How does this source code differ than what's in the course?

In the course we build up a 4,000+ line Flask application in 15 stages while
I'm at your side explaining my thought process along the way. You will get to
see the source code grow from a single `app.py` file to a large code base that
spans across dozens of files and folders.

#### This repo includes up to the 6th stage. By this point in the code base, you'll be introduced to concepts such as:

- Using Docker to "Dockerize" a multi-service Flask app
- Using Flask extensions
- Flask blueprints
- Jinja templates
- Working with forms
- Sending e-mails through Celery
- Testing and analyzing your code base

#### The rest of the course covers topics such as:

- A crash course on Docker and Docker Compose (including multi-stage builds)
- Going over the application's architecture and tech choices
- Creating a full blown user management system
- Creating a custom admin dashboard
- Logging, middleware and error handling
- Using Click to create custom CLI commands
- Accepting recurring credit card payments with Stripe
- Building up a dice game called "Snake Eyes"
- Responding with JSON from Flask and creating AJAX requests
- Processing microtransaction payments with Stripe
- Dealing with database migrations
- Converting your app to support multiple languages (i18n)
- A crash course on Webpack, ES6 JavaScript and SCSS

**By the time you finish the course, you'll have all the confidence you need to
build a large web application with Flask**.

---

There's over 187 video lessons, 25+ hours of content, coding exercises and an
e-book that's included. You also get free updates for life as well as life time
support. I've added 15+ hours of free updates over the years.

These updates range from adding new features like Webpack to keeping Python,
Node and all package / service versions up to date. There's even 1 update
that's a 5 hour live recording where I updated a bunch of things at once. This
includes using git too (making good commits, interactive rebasing, etc.), live
debugging and Googling for errors.

Also as a bonus, there's an additional 18 video lessons and 3 hours of content
that covers building a separate RESTful API driven application that uses
websockets.

**Everything you'd want to know about the course can be found here:**  
[https://buildasaasappwithflask.com](https://buildasaasappwithflask.com/?utm_source=github&utm_medium=bsawf&utm_campaign=readme-bottom)
