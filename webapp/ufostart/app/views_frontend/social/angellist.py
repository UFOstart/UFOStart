import logging, urllib, simplejson
from httplib2 import Http
from operator import attrgetter

from hnc.apiclient import Mapping, BooleanField, TextField, DictField, IntegerField, ListField

from ufostart.lib.html import getYoutubeVideoId, getVimeoVideoId
from ufostart.app.views_frontend.social import AbstractSocialResource, SocialNetworkException, UserRejectedNotice
from ufostart.app.models.auth import SocialNetworkProfileModel

log = logging.getLogger(__name__)



class MarketModel(Mapping):
    id = IntegerField()
    tag_type = TextField()
    name = TextField()
    display_name = TextField()


class ScreenShotModel(Mapping):
    thumb = TextField()
    original = TextField()

    def __repr__(self):
        return self.original

class CompanyRolePerson(Mapping):
    name = TextField()
    high_concept = TextField()
    bio = TextField()
    angellist_url = TextField()
    thumb_url = TextField()

class CompanyModel(Mapping):
    id = IntegerField()
    token = TextField()

    name = TextField()
    display_name = TextField()
    high_concept = TextField()
    product_desc = TextField()
    logo_url = TextField()
    thumb_url = TextField()
    video_url = TextField()
    company_url = TextField()
    angellist_url = TextField()
    markets = ListField(DictField(MarketModel))
    screenshots = ListField(DictField(ScreenShotModel))
    pledges = ListField(DictField(ScreenShotModel))

    @property
    def display_name(self):
        return self.name
    @property
    def display_description(self):
        return self.high_concept

    @property
    def display_tags(self):
        return map(attrgetter("display_name"), self.markets)

    def getYoutubeVideoId(self):
        if self.video_url and 'youtube' in self.video_url:
            return getYoutubeVideoId(self.video_url)
        return ''

    def getVimeoVideoId(self):
        if self.video_url and 'vimeo' in self.video_url:
            return getVimeoVideoId(self.video_url)
        return ''

    def getFirstScreenShot(self):
        try:
            return self.screenshots[0].original
        except IndexError:
            return None

class CompanyRoleModel(Mapping):
    confirmed = BooleanField()
    role = TextField()
    hidden = BooleanField()
    startup = DictField(CompanyModel)
    tagged = DictField(CompanyRolePerson)

    def getPicture(self):
        return self.tagged.thumb_url or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    def getPersonUrl(self):
        return self.tagged.angellist_url
    def getPersonName(self):
        return self.tagged.name
    def getPersonDescr(self):
        return self.tagged.bio or ''




class SocialResource(AbstractSocialResource):
    @property
    def site_title(self):
        return ['Angellist Import', self.request.globals.project_name]
    getCodeEndpoint = "https://angel.co/api/oauth/authorize"
    codeEndpoint = "https://angel.co/api/oauth/token"
    profileEndpoint = "https://api.angel.co/1/me"
    companiesEndpoint = "https://api.angel.co/1/startup_roles"
    companyEndpoint = "https://api.angel.co/1/startups/{company_id}"
    companyRolesEndpoint = "https://api.angel.co/1/startups/{company_id}/roles"

    def loginStart(self, request):
        self.start_process(request)
        params = {'response_type':"code"
                    , 'client_id':self.settings.appid
                    , 'scope':'email'
                 }
        request.fwd_raw("{}?{}".format(self.getCodeEndpoint, urllib.urlencode(params)))

    def getAuthCode(self, request):
        code = request.params.get("code")
        if not code:
            return False

        params = {'grant_type':'authorization_code', 'code':code
                    , 'client_id':self.settings.appid, 'client_secret':self.settings.appsecret
                 }

        h = Http(**self.settings.http_options)
        return h.request( "{}?{}".format(self.codeEndpoint, urllib.urlencode(params)), method="POST", body = {} )

    def getTokenProfile(self, content):
        h = Http(**self.settings.http_options)
        result = simplejson.loads(content)
        access_token = result['access_token']
        return access_token, h.request('{}?{}'.format(self.profileEndpoint, urllib.urlencode({'access_token':access_token})), method="GET")

    def getProfileFromData(self, token, data, context, request):
        profile = simplejson.loads(data)
        return SocialNetworkProfileModel(
                network = 'angellist'
                , id = profile['id']
                , accessToken = token
                , picture = profile.get('image', "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm")
                , email = profile['email']
                , name = profile['name']
            )

    def getProfile(self, request):
        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice("Import failed")
            else:
                return None
        resp, content = self.getAuthCode(request)
        if resp.status == 500:
            raise SocialNetworkException("Import failed")
        if resp.status != 200:
            result = simplejson.loads(content)
            return None
        else:
            token, (resp, data) = self.getTokenProfile(content)
            if resp.status == 500:
                raise SocialNetworkException("Import failed")
            if resp.status != 200:
                result = simplejson.loads(data)
                return None
            else:
                return self.getProfileFromData(token, data, request.root, request)

    def unwrapCompanies(self, data):
        result = simplejson.loads(data)
        def wrap(json):
            if json['startup'].get("hidden"):
                return None
            else:
                return CompanyRoleModel.wrap(json)
        return filter(None, map(wrap, result['startup_roles']))

    def getCompaniesData(self, user_id, token):
        h = Http(**self.settings.http_options)
        resp, data = h.request('{}?{}'.format(self.companiesEndpoint, urllib.urlencode({'access_token':token, 'v':'1', 'user_id':user_id})), method="GET")
        if resp.status == 500:
            raise SocialNetworkException()
        if resp.status != 200:
            return None
        else:
            return self.unwrapCompanies(data)

    def getCompanyData(self, company_id, token):
        h = Http(**self.settings.http_options)
        resp, data = h.request(self.companyEndpoint.format(company_id = company_id), method="GET")
        if resp.status == 500:
            raise SocialNetworkException()
        if resp.status != 200:
            return None
        else:
            return CompanyModel.wrap(simplejson.loads(data))


    def getCompanyRoles(self, company_id, token):
        h = Http(**self.settings.http_options)
        resp, data = h.request(self.companyRolesEndpoint.format(company_id = company_id), method="GET")
        if resp.status == 500:
            raise SocialNetworkException()
        if resp.status != 200:
            return None
        else:
            result = simplejson.loads(data)
            return map(CompanyRoleModel.wrap, result['startup_roles'])