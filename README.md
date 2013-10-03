UFOstart
========

This is a python pyramid project. It is recommended to run it from a virtual environment with Python 2.7.

The instructions are written with windows in mind, all steps apply in Linux as well, but YMMV.

To get a local test environment running you should do the following:


To install all requirements and dependencies, do the following from the repository root folder:

    virtualenv --no-site-packages env
    cd webapp
    ..\env\Scripts\python setup.py develop

Note that <code>env</code> is already in the <code>.gitignore</code>.

With this you are basically set to go.
To bring up a development server execute the following from within the <code>/webapp</code> folder (i.e. where your ini file is located):

    ..\env\Scripts\paster serve --reload local.ini

Please note that the standard local.ini file requires a Redis instance and an API running somewhere.


Configuring API Server
----------------------------------------

To get any app running you will need a webapi running somewhere.

Configure the API location via:
    deploy.api.url = https://dev.api.raftcarinthia.com
    deploy.api.version = 0.0.1

And set the authentication token for each of the front ends via:

    website.apiToken = 3C5EE0CB-A119-4AAF-BFD6-30F91609FA8E

This sets the client token for the frontend called "website".


You can find out where these settings get set by looking at each <code>Views..../__init__.py</code> module and check this block:

    def includeme(config):
        settings = config.registry.settings
        settings['g'].setSettings(WebsiteSettings, settings)

This registers the settings into the context and makes them acessible throughout a request life cycle.




Configuring caching and session backends
----------------------------------------

You can configure your cache backend by editing the following in your ini file:

    cache.backend = dogpile.cache.redis
    cache.arguments.host = 127.0.0.1
    cache.arguments.port = 6379
    cache.arguments.db = 1

Find out all backends supported for caching by reading through the <a href="http://dogpilecache.readthedocs.org/en/latest/">dogpile docs</a>.

Session storage is by default just locally in the file system (in redis on production systems). Change it by editing the following lines:

    session.data_dir = %(here)s/../data/sess
    session.type = file


If you find strange errors on form submission, i.e. you cannot log in, it wont remember anything done, the sessions dont change, then most likely ou have not set the cookie domain correctly.
Set it to localhost for development or configure any local webserver to host that very domain you are hosting the app on:

    session.cookie_domain = local.webenvironment.com

Look up the <a href="http://beaker.readthedocs.org/en/latest/sessions.html">Beaker sessions docs</a> for more info.


