from pyramid.decorator import reify
from ufostart.lib.baseviews import RootContext
from ufostart.website.apps.auth import LoginForm
from ufostart.website.apps.models.auth import AnonUser

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


class WebsiteRootContext(RootContext):
    static_prefix = "/web/static/"
    app_label = 'website'

    @reify
    def loginFormWithValues(self):
        return LoginForm, {}, {}

    @reify
    def user(self):
        return self.request.session.get(USER_SESSION_KEY) or AnonUser()

    def setUser(self, user):
        self.request.session[USER_SESSION_KEY] = self.user = user
        return user

    def logout(self):
        if USER_SESSION_KEY in self.request.session:
            del self.request.session[USER_SESSION_KEY]
        self.user = AnonUser()

    def getPostLoginUrlParams(self):
        if self.user.isAnon():
            return "website_index", [], {}
        else:
            return "website_signup_decision", [], {}



stdRequireLogin = logged_in(lambda req: req.fwd_url("website_index", _query=[("furl", req.url)]))
fwdRequireLogin = lambda route: logged_in(lambda req: req.fwd_url("website_index", _query=[("furl", route(req))]))

class WebsiteAuthContext(WebsiteRootContext):
    def is_allowed(self, request):
        if not self.user.isAnon():
            request.fwd_raw(request.furl)



class WebsiteAuthedContext(WebsiteRootContext):
    def is_allowed(self, request):
        if self.user.isAnon():
            request.fwd("website_index", _query=[('furl', request.url)])
        li_profile = self.user.profileMap.get('linkedin')
        if not li_profile or not li_profile.id:
            request.fwd("website_require_li", _query=[('furl', request.url)])




