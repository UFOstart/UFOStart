from hnc.tools.generic_views import logout_func
from pyramid.decorator import reify
from pyramid.security import DENY_ALL, ALL_PERMISSIONS, Allow, NO_PERMISSION_REQUIRED
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.admin import handlers
from ufostart.admin.auth import AuthenticationHandler, AdminUserModel, USER_TOKEN, getUser, setUserF, canEdit




class AdminSettings(object):
    key = "admin"
    css_name = 'site_admin'
    static_prefix = "/static/"
    def __init__(self, settings):
        self.login = settings['login']



class BaseAdminContext(BaseContextMixin):
    app_label = 'admin'
    __acl__ = [(Allow, "AdminUser", ALL_PERMISSIONS), DENY_ALL]
    __auth_template__ = "ufostart:templates/auth/login.html"

    canEdit = reify(canEdit)
    user = reify(getUser)
    setUser = setUserF
    site_title = ['Admin Site']
    workflow = None
    @reify
    def settings(self):
        return getattr(self.request.globals, self.app_label)

    @property
    def main_menu(self):
        return self.get_main_area().children.items()

class AdminContext(BaseAdminContext):
    children = {}
    def __getitem__(self, item):
        return self.children[item](self, item)


def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(AdminSettings, settings)

    config.add_view(handlers.index                           , context = AdminContext                        , renderer = "ufostart:templates/admin/index.html")
    config.add_forbidden_view(AuthenticationHandler          , containment = AdminContext                    , renderer = "ufostart:templates/admin/form.html")
    config.add_view(logout_func(USER_TOKEN, AdminUserModel), name = 'logout', context = AdminContext)