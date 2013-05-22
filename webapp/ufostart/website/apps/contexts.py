from pyramid.decorator import reify
from ufostart.lib.baseviews import RootContext

USER_SESSION_KEY = 'WEBSITE_USER'

class logged_in(object):
    def __init__(self, auth_route):
        self.auth_route = auth_route
    def __call__(self, wrapped):
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass
        def wrapped_f(obj):
            if obj.context.user.isAnon():
                obj.request.fwd_raw(self.auth_route(obj.request))
            else:
                return wrapped(obj, obj.context, obj.request)
        return wrapped_f


LoginForm = None

class WebsiteRootContext(RootContext):
    static_prefix = "/web/static/"
    app_label = 'website'

    @reify
    def loginFormWithValues(self):
        return LoginForm, {}, {}


    @reify
    def user(self):
        return None
    def setUser(self, user):
        self.user = user
        self.request.session[USER_SESSION_KEY] = user
        return user
    def logout(self):
        if USER_SESSION_KEY in self.request.session:
            del self.request.session[USER_SESSION_KEY]


stdRequireLogin = logged_in(lambda req: req.fwd_url("website_signup", _query=[("furl", req.url)]))
fwdRequireLogin = lambda route: logged_in(lambda req: req.fwd_url("website_signup", _query=[("furl", route(req))]))


class WebsiteAuthedContext(WebsiteRootContext):
    def is_allowed(self, request):
        if self.user.isAnon():
            request.fwd("website_signup", _query=[('furl', request.url)])