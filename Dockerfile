# Use the barebones version of Python 2.7.10.
FROM python:2.7.10-slim
MAINTAINER Nick Janetakis <nick.janetakis@gmail.com>

# Install any packages that must be installed.
RUN apt-get update && apt-get install -qq -y build-essential nodejs nodejs-legacy npm libpq-dev postgresql-client-9.4 libpng-dev --fix-missing --no-install-recommends

# Setup the install path for this service.
ENV INSTALL_PATH /catwatch
RUN mkdir -p $INSTALL_PATH

# Update the workdir to be where our app is installed.
WORKDIR $INSTALL_PATH

# Ensure packages are cached and only get updated when necessary.
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Ensure frontend packages are cached and only get updated when necessary.
COPY package.json package.json
RUN npm install

# Copy the source from the build machine to the image at the WORKDIR path.
COPY . .

# Process all of the assets.
RUN PUBLIC_PATH='/' NODE_ENV='production' npm run-script build

# Give access to the CLI script.
RUN pip install --editable .

# Create a volume so that nginx can read from it.
VOLUME ["$INSTALL_PATH/build/public"]

# The default command to run if no command is specified.
CMD gunicorn -b 0.0.0.0:8000 "catwatch.app:create_app()"
