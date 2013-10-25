from fabric.api import run, sudo
from fabric.context_managers import cd
from fabric.contrib import files
from fabric.operations import put

SYSTEM_PACKAGES = ["sudo"
                  , "build-essential"
                  , "libjpeg62-dev"
                  , "libxml2-dev"
                  , "libxslt1-dev"
                  , "unzip"
                  , "libpng12-dev"
                  , "libfreetype6-dev"
                  , "libpcre3-dev"
                  , "libpcre3-dev"
                  , "libssl-dev"
                  , "apache2-utils"
                  , "lib32bz2-dev"
                  , "curl"
                  , "libreadline6"
                  , "libreadline6-dev"
                  , "libmhash2"
                  , "libmhash-dev"
                  , "libmcrypt4"
                  , "libtomcrypt-dev"
                  , "libssl-dev"
                  , "libevent-dev"
                  , "git"]

VERSIONS = {
    "PYTHON":"2.7.5"
    , "NGINX":"1.5.6"
}
KEYS = [
  "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCj5VP8RzFPkkN+43Wmg0aN9T5XJKmx0+nBdbr+CKE3xukYkm8Hwg8lTaRQQOFWCiYAH7oxf9g0bT/Vp5a7uDok6Eh9ETPlIle0G+iikh3y+faQmuXbfCxj1Mielgf2Q/tHR6YsS50wfvyBE+hvMWtw54LY/BfoSTkZx5hWF40UcSKA7FvZwC0zbTvyrCczpliPdogazHzTNkmNu2v8QQvxRjg50RNHJI4ECKWUn/WjQUmgJOcnNKisHsK3RdI2joXhrLg86K1ndT2k7shGb7uNElEY0g0/BnEA9tVwJq5dHclJiU72ocuVbC/p4HE1R+DZxiazZhYSJ363yhgLjocL www-data@bellerophon"
]


def set_resolv():
    run("""
echo "# nameserver config
nameserver 8.8.8.8
nameserver 213.133.100.100
nameserver 213.133.98.98
nameserver 213.133.99.99" > /etc/resolv.conf
    """)


def set_host(name):
    run("cp /etc/hosts /etc/hosts.bak")
    run("""
sed -e 's/Debian-.*-64-minimal/{host}/g' /etc/hosts.bak > /etc/hosts
echo Welcome to {host}> /etc/motd
echo {host} > /etc/hostname
    """.format(host=name))


def adduser():
    name = "mpeschke"
    run("adduser {}".format(name))
    with cd("/home/mpeschke"):
      sudo("mkdir .ssh", user="mpeschke")
      sudo("ssh-keygen -t rsa -b 4096", user="mpeschke")
      sudo("cp .ssh/id_rsa.pub .ssh/authorized_keys", user="mpeschke")

def set_wwwuser():
    sudo("mkdir /home/www-data")
    sudo("chown www-data: /home/www-data")
    sudo("usermod -d /home/www-data -s /bin/bash www-data")
    with cd("/server"):
      sudo("chown -R www-data: www")
    with cd("/home/www-data"):
      sudo("mkdir .ssh", user = 'www-data')
      sudo("ssh-keygen -t rsa -b 4096", user = 'www-data')
      sudo("cp .ssh/id_rsa.pub .ssh/authorized_keys", user = 'www-data')
    files.append("/home/www-data/.ssh/authorized_keys","\n".join(KEYS), use_sudo=True)

def update():
    sudo("mkdir /server/{src,www} -p")
    sudo("apt-get update")
    sudo("apt-get install -y {}".format(" ".join(SYSTEM_PACKAGES)))


def add_python():
    with cd("/server/src"):
        sudo("wget http://www.python.org/ftp/python/{0}/Python-{0}.tar.bz2".format(VERSIONS['PYTHON']))
        sudo("tar xfvj Python-{}.tar.bz2".format(VERSIONS['PYTHON']))
    with cd("/server/src/Python-{}".format(VERSIONS['PYTHON'])):
        sudo("./configure && make && make install")
        sudo("wget http://peak.telecommunity.com/dist/ez_setup.py")
        sudo("python ez_setup.py")
        sudo("easy_install virtualenv Cython ctypes")


def set_nginx_startup():
    files.upload_template("nginx.initd.tmpl", "/etc/init.d/nginx", {'NGINX_VERSION': VERSIONS['NGINX']}, use_sudo=True)
    sudo("chmod +x /etc/init.d/nginx")
    sudo("update-rc.d nginx defaults")

def set_nginx_conf():
    sudo("mkdir -p /server/nginx/etc/{sites.enabled,sites.disabled}")
    files.upload_template("nginx.conf.tmpl", "/server/nginx/etc/nginx.conf", VERSIONS, use_sudo=True)
    sudo("/etc/init.d/nginx reload")
    
def add_nginx():
    with cd("/server/src"):
        sudo("wget http://nginx.org/download/nginx-{}.tar.gz".format(VERSIONS['NGINX']))
        sudo("tar xfv nginx-{}.tar.gz".format(VERSIONS['NGINX']))
    with cd("/server/src/nginx-{}".format(VERSIONS['NGINX'])):
        sudo("./configure \
            --group=www-data\
            --user=www-data\
            --with-http_ssl_module\
            --prefix=/server/nginx/{}\
            --conf-path=/server/nginx/etc/nginx.conf\
            --error-log-path=/server/nginx/logs/error.log\
            --pid-path=/server/nginx/run/nginx.pid\
            --lock-path=/server/nginx/run/nginx.lock\
            --with-http_gzip_static_module && make && make install".format(VERSIONS['NGINX']))
    set_nginx_startup()
    set_nginx_conf()


def setup():
    update()
    add_nginx()
    add_python()
    set_wwwuser()