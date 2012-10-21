hubway-challenge
================

Exploring the hubway data challenge with [django](https://www.djangoproject.com/) and [d3.js](http://d3js.org/)

Requirements
------------

  * python-dev: Development headers for the python programming language.
  * libpq-dev: This is required by the psycopg2 python library.
  * postgresql-client: Specifically, the 'psql' program for creating databases.

Installation
------------

Recommended installation is with virtualenv. The following instructions install virtualenv, 
activate the environment, and start the system.

  1. Install virtualenv in your system's python path:

    > easy_install virtualenv
  
  2. Create a new virtual environment (this one is called 'env'):

    > virtualenv env

  3. Activate the virtual environment:

    > . env/bin/activate
  
  4. Install the pre-requisites:

    > pip install -r requirements.txt
    
  5. With all the requirements satisfied, create the database:

    > psql -c "create role hubway with password 'hubway' login;" -U postgres
    > psql -c "create database hubwayapp with owner hubway;" -U postgres
    
  7. Set the environment variable used to connect to the database (assuming a bash shell):

    > export DATABASE_URL=postgres://hubway:hubway@localhost/hubwayapp
    
  6. With the database created, create the database schema and load the initial data (1% of all trips):

    > hubway/manage.py syncdb
    
  7. With the database created and the data loaded, you are ready to start the development server:

    > hubway/manage.py runserver
    
    
Deployment
----------

The application is deployed on heroku, and uses the [heroku toolbelt](https://toolbelt.heroku.com/) 
to perform deployments.

When running your app, the heroku toolbelt looks for a local file ".env". This contains the environment variables
required for the application. It contains two local settings:

  1. DATABASE_URL
  2. PORT

An example of this file:

    DATABASE_URL=postgres://hubway:hubway@localhost/hubwayapp
    PORT=8000
    
Create this file, and you will be able to deploy the application locally with `foreman`:

    > foreman start
    
This will start the production configuration of the application on your local system.


Using All The Data
------------------

In order to use all the data (the above steps only install 1% of the hubway challenge data), you must truncate
the `trip` table, and load the full_data.json data fixture:

    > psql -c "truncate table hubway.trips;" -U postgres hubwayapp
    > DATABASE_URL=postgres://hubway:hubway@localhost/hubwayapp hubway/manage.py loaddata full_data
    
This is a large set of data, and takes a while to load. There are 552,073 trips in the data, so give it a
few minutes to load. It takes 10 minutes or more on my laptop.