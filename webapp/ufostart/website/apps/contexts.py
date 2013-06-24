import logging
import urllib
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
import simplejson
from ufostart.lib.baseviews import RootContext
from ufostart.website.apps.models.auth import AnonUser
from ufostart.website.apps.models.procs import GetCompanyProc

USER_SESSION_KEY = 'WEBSITE_USER'

log = logging.getLogger(__name__)

class WebsiteRootContext(RootContext):
    static_prefix = "/web/static/"
    app_label = 'website'

    @reify
    def user(self):
        return self.request.session.get(USER_SESSION_KEY) or AnonUser()
    def userURL(self, token):
        if token == self.user.token:
            return self.request.fwd_url("website_user_home")
        else:
            return self.request.fwd_url("website_user", slug = token)

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

    @reify
    def location(self):
        cache = self.request.globals.cache
        ip = self.request.client_addr
        location = cache.get('HOSTIP_{}'.format(ip))
        if not location:
            try:
                response = urllib.urlopen('http://api.hostip.info/get_json.php?ip={}&position=true'.format(ip)).read()
                result = simplejson.loads(response)
                location = '{city}, {country_name}'.format(**result)
                cache.set('HOSTIP_{}'.format(self.request.client_addr), location)
            except:
                pass
        return location

    def __getitem__(self, item):
        if item in self.settings.networks:
            return self.settings.networks[item]


class WebsiteAuthContext(WebsiteRootContext):
    def is_allowed(self, request):
        if not self.user.isAnon():
            request.fwd_raw(request.furl)



class WebsiteCompanyContext(WebsiteRootContext):
    @reify
    def company(self):
        company = GetCompanyProc(self.request, {'slug': self.request.matchdict['slug']})
        if not company:
            self.user.Company = None
        return company

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
            return needMap.get(self.request.matchdict['need'])
        else: return None

    @reify
    def isTeamMember(self):
        return self.company.isMember(self.user.token)
    @reify
    def canEditCompany(self):
        token = self.user.token
        company = self.company
        return company.isFounder(token) or company.isMentor(token)
    @reify
    def canAskForApproval(self):
        return self.company.isFounder(self.user.token)
    @reify
    def canApproveCompany(self):
        return self.company.isMentor(self.user.token)

class WebsiteCompanyFounderContext(WebsiteCompanyContext):
    def is_allowed(self, request):
        if self.user.isAnon():
            request.fwd("website_login", request.furl)
        if not self.canEditCompany:
            raise HTTPForbidden()


