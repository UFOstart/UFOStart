from collections import OrderedDict
from hnc.apps.static_content.views import set_up_content_mgmt_app, delete_view_factory, ContentEditViewFactory, ContentCreationViewFactory, KeyValueModel
from hnc.tools.generic_views import logout_func
from pyramid.decorator import reify
from pyramid.security import DENY_ALL, ALL_PERMISSIONS, Allow
from ufostart.lib.baseviews import BaseContextMixin
from ufostart.admin import handlers
from ufostart.admin.auth import AuthenticationHandler, AdminUserModel, USER_TOKEN, getUser, setUserF, canEdit
from ufostart.models.procs import AdminTemplatesGetProc, AdminNeedGetProc, AdminServiceGetProc, GetStaticContentProc, SetStaticContentProc


class AdminSettings(object):
    key = "admin"
    css_name = 'site_admin'
    static_prefix = "/static/"

    def __init__(self, settings):
        self.login = settings['login']
        self.filepickerKey = settings['filepickerKey']



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






class SingleTemplateContext(BaseAdminContext):
    def __getitem__(self, item):
        raise KeyError()
    @reify
    def template(self):
        return AdminTemplatesGetProc(self.request, {'key':self.__name__})
class TemplatesContext(BaseAdminContext):
    menu_label = "Templates"
    def __getitem__(self, item):
        if item in ['create']:
            raise KeyError()
        else:
            return SingleTemplateContext(self, item)





class SingleTaskContext(BaseAdminContext):
    def __getitem__(self, item):
        raise KeyError()

    @reify
    def task(self):
        return AdminNeedGetProc(self.request, {'key':self.__name__})
class TaskContext(BaseAdminContext):
    menu_label = "Tasks"
    def __getitem__(self, item):
        if item in ['create']:
            raise KeyError()
        else:
            return SingleTaskContext(self, item)





class SingleServiceContext(BaseAdminContext):
    def __getitem__(self, item):
        raise KeyError()
    @reify
    def service(self):
        return AdminServiceGetProc(self.request, {'name':self.__name__})
class ServiceContext(BaseAdminContext):
    menu_label = "Services"
    def __getitem__(self, item):
        if item in ['create']:
            raise KeyError()
        else:
            return SingleServiceContext(self, item)








class SingleContentContext(BaseAdminContext):
    def __getitem__(self, item):
        raise KeyError()
    @reify
    def content(self):
        return KeyValueModel(key = self.__name__, value = self.contentsMap[self.__name__])

    @property
    def contentsMap(self):
        return self.__parent__.contentsMap

class ContentContext(BaseAdminContext):
    menu_label = "Contents"
    def __getitem__(self, item):
        if item in ['create', 'active']:
            raise KeyError()
        else:
            return SingleContentContext(self, item)

    @reify
    def contentsMap(self):
        result = GetStaticContentProc(self.request)
        return {k.key:k.value for k in result.Static}








class AdminContext(BaseAdminContext):
    children = OrderedDict([
        ('template', TemplatesContext)
        , ('task', TaskContext)
        , ('service', ServiceContext)
        , ('content', ContentContext)
    ])

    def __getitem__(self, item):
        return self.children[item](self, item)


def dashboard(ctxt, req): return {}


def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(AdminSettings, settings)

    config.add_view(handlers.index                               , context = AdminContext                        , renderer = "ufostart:templates/admin/index.html")
    config.add_forbidden_view(AuthenticationHandler              , containment = AdminContext                    , renderer = "ufostart:templates/admin/form.html")
    config.add_view(logout_func(USER_TOKEN, AdminUserModel)      , name = 'logout', context = AdminContext)

    #=================================================== TEMPLATES =====================================================
    config.add_view(handlers.index                               , context = TaskContext                         , renderer = "ufostart:templates/admin/tasks.html")
    config.add_view(handlers.TaskCreateHandler, name="create"    , context = TaskContext                         , renderer = "ufostart:templates/admin/form.html")
    config.add_view(handlers.TaskEditHandler  , name="edit"      , context = SingleTaskContext                   , renderer = "ufostart:templates/admin/form.html")

    config.add_view(handlers.index                               , context = ServiceContext                      , renderer = "ufostart:templates/admin/services.html")
    config.add_view(handlers.ServiceCreateHandler, name="create" , context = ServiceContext                      , renderer = "ufostart:templates/admin/form.html")
    config.add_view(handlers.ServiceEditHandler  , name="edit"   , context = SingleServiceContext                , renderer = "ufostart:templates/admin/form.html")

    config.add_view(handlers.index                               , context = TemplatesContext                    , renderer = "ufostart:templates/admin/templates.html")
    config.add_view(handlers.TemplateCreateHandler, name="create", context = TemplatesContext                    , renderer = "ufostart:templates/admin/form.html")
    config.add_view(handlers.TemplateEditHandler  , name="edit"  , context = SingleTemplateContext               , renderer = "ufostart:templates/admin/form.html")



    def dictionary_factory(request):
        result = GetStaticContentProc(request)
        return {k.key:k.value for k in result.Static}


    POFILE = set_up_content_mgmt_app(config, "ufostart:locale/ufostart.pot", dictionary_factory)

    # helper view
    def get_active_keys(ctxt, req):
            return [l.msgid for l in POFILE()]

    config.add_view(dashboard                                                       , context = ContentContext      , renderer = "ufostart:templates/admin/contents.html")
    config.add_view(ContentCreationViewFactory(SetStaticContentProc), name="create" , context = ContentContext      , renderer = "ufostart:templates/admin/form.html")
    config.add_view(get_active_keys                                 , name="active" , context = ContentContext      , renderer = "json")
    config.add_view(ContentEditViewFactory(SetStaticContentProc)    , name="edit"   , context = SingleContentContext, renderer = "ufostart:templates/admin/form.html")
    config.add_view(delete_view_factory(SetStaticContentProc)       , name="delete" , context = SingleContentContext)