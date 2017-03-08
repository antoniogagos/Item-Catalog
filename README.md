# Item-Catalog

This is a python module that creates a website and JSON API for a list of items grouped into a category. Users can edit or delete items they've created. Adding, deleting and editing items requires logging in with Google+.

  * Routing and Templating made with <b>Flask</b>
  * Uses <b>SQLAlchemy</b> to communicate with the back-end db
  * <b>RESTful API</b> endpoints that return json files
  * Uses <b>Google Login</b> to authenticate users

## How to run it

  * Install Vagrant.
  * Then, install the dependency libraries
  * Seeding the database: <code>python database_setup.py</code>
  * Run <code>python project.py</code>
  * Then access the site going to <code>localhost:5000</code>
