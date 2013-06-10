from hnc.forms.messages import GenericErrorMessage
from pyramid.decorator import reify
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
        if user.isAnon():
            return "website_index", [], {}
        elif user.Company and user.Company.slug:
            return "website_company", [], {'slug':user.Company.slug}
        else:
            return "website_index", [], {}


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
        return {'slug': self.request.matchdict['slug']}


class RoundContext(WebsiteCompanyContext):
    @reify
    def need(self):
        return self.company.Round

class NeedContext(RoundContext):
    @reify
    def need(self):
        needMap = {n.key:n for n in self.company.Round.Needs}
        return needMap[self.request.matchdict['need']]

    @reify
    def urlArgs(self):
        return {'slug': self.request.matchdict['slug'], 'need': self.need.key}
