UFOstart Provisioning
=====================

Use the ufostartweb image from azure to setup a new virtual box. During the process you are asked to upload your SSH key.

See <a href="http://www.windowsazure.com/en-us/manage/linux/how-to-guides/ssh-into-linux/">the documentation</a> for instructions on how to generate a key.

During the azure setup you can choose whatever options you like, just make sure to select SSL, HTTP and HTTPS tunnels to your webserver. See <a href="AZURE.md">screenshots here</a>.

Use putty or your favourite ssh client to connect to the virtual machine as you configured it.

Notice azureuser is a sudoer but not a superuser, i.e. can do <code>sudo so</code> at any time.


VM Setup
--------

When you have connected to the machine:

Clean up Redis first:

    redis-cli
    flushall


Then clean up the NGINX config:

    sudo su
    rm /server/nginx/logs/*
    cd /server/nginx/etc/sites.enabled
    rm ufostart.com.live.conf
    cat > ufostart.com.dev.conf
  
  
Edit the file <code>ufostart.com.dev.conf</code> to reflect your staging environment <code>basepath</code> and <code>url</code>.

A sample config could be the following (YMMV):

    upstream ufostart_dev {
       # check your python config where it is running and which port
       server 127.0.0.1:6545;
    }
    server {
        listen   80;

        set $ENVIRONMENT dev;
        set $base /server/www/ufostart/$ENVIRONMENT/code/current/ufostart;

        location /favicon.ico {expires 30d;alias $base/static/img/favicon.ico;}
        location /robots.txt {expires 30d; alias $base/static/robots.txt;}
        location /static/ {expires 30d;alias $base/static/;}

        location /api/ {
            # these need to be configured inline, as proxy_pass does not like variables much
            proxy_set_header Host API_HOST;
            proxy_set_header Client-Token API_CLIENT_TOKEN;
            proxy_pass https://API_HOST/;
        }
        location /net/li/ {
            proxy_set_header x-li-format "json";
            proxy_pass https://api.linkedin.com/v1/;
        }
        location / {
            add_header "X-UA-Compatible" "IE=Edge,chrome=1";
            proxy_set_header        Host $host;
            proxy_set_header        X-Real-IP $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header        X-Forwarded-Proto $scheme;
            proxy_pass http://ufostart_dev/;
        }
    }

When your done, dont forget to reload the nginx config:

    /etc/init.d/nginx reload


Now lets setup a staging environment called "dev":

    sudo su - www-data
    cd /server/wwww/ufostart
    rm -rf live
    mkdir dev
    
You need to make sure that the <code>www-data</code> user is set up to accept your ssh key. 
I.e. add your public ssh key to <code>/home/www-data/.ssh/authorized_keys</code>.
If you dont have a ssh key yet, generate it with the <a href="https://help.github.com/articles/generating-ssh-keys">github instructions</a>. 
Make sure you have the resulting <code>id_rsa</code> file available on the build machine.


Standard VM Layout
------------------

The VMs are stock Ubuntu 12.04LTS instances with the latest: nginx, python and redis installed.

Nginx is located in:

    /server/nginx
    
Nginx configuration:

    /server/nginx/etc/sites.enabled/*.conf

Nginx config changes reload:

    /etc/init.d/nginx reload
  
  
Redis is in

    /etc/redis
  
Flush redis with:

    redis-cli
    flushall

Restart redis with:

    /etc/init.d/redis-server restart

Python is installed system wide. Each environment uses a virtualenv in {BASE_PATH}/env.


All projects should live in

    /server/www
  
and are owned by <code>www-data</code>.


The python webservers are managed by <a href="http://supervisord.org/">Supervisor</a>. Restart the webserver via:

    sudo su - www-data
    cd /server/www/{PROJECT_NAME}/{ENV_NAME}
    ./env/bin/supervisorctl -c supervisord.cfg restart all
    
Shut it down by: 

    sudo su - www-data
    cd /server/www/{PROJECT_NAME}/{ENV_NAME}
    ./env/bin/supervisorctl -c supervisord.cfg shutdown
    

Or via init script:

    sudo su
    /etc/init.d/super_ufostart stop
    /etc/init.d/super_ufostart start
    


Environment Setup
-----------------

Environment setup and deployment are automated with <a href="http://docs.fabfile.org/en/latest/">python fabric</a>.
    
With fabric execute the following from your working copy / build server working copy:

    cd deploy
    fab -H SERVER_DOMAIN -u www-data -i WWW_DATA_SSHKEY create_env:env=live

    
Environment Layout
-----------------

Usually in 

    /server/www/{PROJECT_NAME}/{ENV_NAME}
    
you will find

- <code>supervisor.cfg</code>: the config file for the python web server monitor / manager (<a href="http://supervisord.org/">Supervisor</a>)
- <code>run</code>: contanis supervisor.pid and socket
- <code>logs</code>: contanis supervisor logs and python webserver logs
- <code>env</code>: contains the python virtual environment
- <code>repo.git</code>: contains the git working copy from which to build
- <code>code</code>: contains all old and current web app builds

The currently running code is located at:

    /server/www/{PROJECT_NAME}/{ENV_NAME}/code/current

    

Deployment
----------
    
Create a development environment and deploy with

    mkdir -p '/server/wwww/ufostart'
    fab -H SERVER_DOMAIN -u www-data -i WWW_DATA_SSHKEY deploy:env=dev

    
If you want to learn everything about what gets deployed how, checkout the <code>fabfile.py</code> in the <code>deploy</code> folder.


CONFIGURATION
-------------

Please see the <a href="README.md">readme</a> on how to configure a webserver instance.


TROUBLESHOOTING
---------------

1. I cannot login!
    Please verify that your ini-config file contains the correct domain for <code>session.cookie_domain = SERVER_DOMAIN</code>

2. My staging environment should not be called "dev", how can I change it?
    There is only few references to dev which you need to change in order to deploy to any environment. 
    * Create a config.ini file with the name of your environment. I.e. dev.ini or staging.ini
    * In the file <code>deploy/fabfile.py</code> add a configuration for your ideal name to the <code>ENVIRONMENTS</code> variable. Note that process groups has a relationship with your ini file, this is expressed in the <code>supervisor.cfg</code> on the server.

3. During my first deploy there was a python package error!
    Probably you found the XLRT issue. It happens. Just run it again.

4. When I browse the website, I sometimes see a red bar at the top. Whats that?
    There is a good chance that your NGINX does not forward the AJAX calls to the API correctly, check your NGINX config around <code>API_HOST</code> and <code>API_CLIENT_TOKEN</code>.
    
    
5. The Api has gone away!
    If your API server is configured by CNAME and has recently changed its IP, be sure to reload nginx config to refresh the IP behind the CNAME.