import logging, os, random
from dogpile.cache import make_region
from hnc.apiclient.backend import VersionedBackend

log = logging.getLogger(__name__)


APP_ROOT = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
VERSION_FILE = os.path.join(APP_ROOT, "VERSION_TOKEN")

if os.path.exists(VERSION_FILE):
    VERSION_TOKEN = open(VERSION_FILE).read().strip()
else:
    VERSION_TOKEN = random.random()
log.info("USING NEW STATIC RESOURCE TOKEN: %s", VERSION_TOKEN)




def get_config_items(config, prefix):
    items = {}
    for key in config.keys():
        if key.startswith(prefix):
            subMap = items
            subKey = key[len(prefix):].strip(".")
            for k in subKey.split(".")[:-1]: subMap = subMap.setdefault(k, {})
            subMap[subKey.split(".")[-1]] = config.get(key)
    return items




class Globals(object):
    mailConfig = {"mail.on":True,"mail.transport":"smtp", "mail.smtp.tls":True}

    def __init__ (self, **settings):
        self.is_debug = settings.get('pyramid.debug_templates', 'false') == 'true'
        self.VERSION_TOKEN = "v={}".format(VERSION_TOKEN)

        backend_options = dict(location = settings['deploy.api.url'], version = settings['deploy.api.version'])
        backend_options['http_options'] = dict( disable_ssl_certificate_validation = True )
        self.backend = VersionedBackend(**backend_options)

        self.project_name = settings['project.name']
        self.site_slogan = settings['project.site_slogan']
        self.secure_scheme = settings['deploy.secure_scheme']

        self.mailConfig.update({"mail.smtp.server":settings['email.host']
            ,"mail.smtp.username":settings['email.user']
            ,"mail.smtp.password":settings['email.pwd']
            ,"mail.smtp.port":settings['email.port']
        })
        self.mailRecipient = settings['email.recipient']

        self.cache = make_region().configure_from_config(settings, "cache.")
        log.info("SETUP CACHE WITH %s", {k:v for k,v in settings.items() if k.startswith("cache.")})


    def getMailConfig(self):
        return self.mailConfig

    def setSettings(self, cls, settings):
        s = cls(get_config_items(settings, cls.key))
        setattr(self, cls.key, s)