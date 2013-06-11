from hnc.forms.messages import GenericErrorMessage
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from ufostart.lib.baseviews import RootContext
from ufostart.website.apps.models.auth import AnonUser
from ufostart.website.apps.models.procs import GetCompanyProc

USER_SESSION_KEY = 'WEBSITE_USER'


class WebsiteRootContext(RootContext):
    static_prefix = "/web/static/"
    app_label = 'website'

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
        user = self.user
        route, args, kwargs = "website_index", [], {}
        if user.Company and user.Company.slug:
            return "website_company", [], {'slug':user.Company.slug}
        if route != self.request.matched_route.name:
            return route, args, kwargs
        else:
            return None, None, None



    def __getitem__(self, item):
        if item in self.settings.networks:
            return self.settings.networks[item]






class WebsiteAuthContext(WebsiteRootContext):
    def is_allowed(self, request):
        if not self.user.isAnon():
            request.fwd_raw(request.furl)



class WebsiteAuthedContext(WebsiteRootContext):
    def is_allowed(self, request):
        if self.user.isAnon():
            request.fwd("website_index", _query=[('furl', request.url)])




class WebsiteCompanyContext(WebsiteRootContext):
    @reify
    def company(self):
        return GetCompanyProc(self.request, {'slug': self.request.matchdict['slug']})

    @reify
    def urlArgs(self):
        if self.need:
            return {'slug': self.request.matchdict['slug'], 'need': self.need.slug}
        else:
            return {'slug': self.request.matchdict['slug']}

    @reify
    def need(self):
        if 'need' in self.request.matchdict:
            needMap = {n.slug:n for n in self.company.Round.Needs}
            return needMap[self.request.matchdict['need']]
        else: return None

    @reify
    def isTeamMember(self):
        return self.company.isMember(self.user.token)

class WebsiteCompanyFounderContext(WebsiteCompanyContext):
    def is_allowed(self, request):
        if self.user.isAnon():
            request.fwd("website_login", request.furl)
        if not self.isTeamMember:
            raise HTTPForbidden()


