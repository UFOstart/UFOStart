import logging
from operator import attrgetter
import urllib
from urlparse import urlparse, parse_qsl
from hnc.apiclient import Mapping, BooleanField, TextField, DictField, IntegerField, ListField
from httplib2 import Http
import simplejson
from ufostart.website.apps.models.auth import SOCIAL_NETWORK_TYPES_REVERSE
from ufostart.website.apps.social import UserRejectedNotice, SocialNetworkException, SocialSettings

log = logging.getLogger(__name__)

class MarketModel(Mapping):
    id = IntegerField()
    tag_type = TextField()
    name = TextField()
    display_name = TextField()


class ScreenShotModel(Mapping):
    thumb = TextField()
    original = TextField()

class CompanyModel(Mapping):
    id = IntegerField()
    name = TextField()
    product_desc = TextField()
    high_concept = TextField()
    logo_url = TextField()
    thumb_url = TextField()
    video_url = TextField()
    company_url = TextField()
    angellist_url = TextField()
    markets = ListField(DictField(MarketModel))
    screenshots = ListField(DictField(ScreenShotModel))

    def getDisplayTags(self):
        return ", ".join(map(attrgetter("display_name"), self.markets))

    def getMedium(self):
        return self.video

    def getVideoId(self):
        scheme, netloc, url, params, query, fragment = urlparse(self.video_url)
        params = dict(parse_qsl(query))
        return params.get('v')

    def getFirstScreenShot(self):
        return self.screenshots[0].original

class CompanyRoleModel(Mapping):
    confirmed = BooleanField()
    role = TextField()
    startup = DictField(CompanyModel)


class AngelListSettings(SocialSettings):
    getCodeEndpoint = "https://angel.co/api/oauth/authorize"
    codeEndpoint = "https://angel.co/api/oauth/token"
    profileEndpoint = "https://api.angel.co/1/me"
    companiesEndpoint = "https://api.angel.co/1/startup_roles"
    companyEndpoint = "https://api.angel.co/1/startups/{company_id}"

    def loginStart(self, request):
        params = {'response_type':"code"
                    , 'client_id':self.appid
                    , 'redirect_uri':request.fwd_url("website_social_login_callback", network = self.type)
                    , 'scope':'email'
                 }
        request.fwd_raw("{}?{}".format(self.getCodeEndpoint, urllib.urlencode(params)))

    def getAuthCode(self, request):
        code = request.params.get("code")
        if not code:
            return False

        params = {'grant_type':'authorization_code', 'code':code
                    , 'redirect_uri':request.fwd_url("website_social_login_callback", network = self.type)
                    , 'client_id':self.appid, 'client_secret':self.appsecret
                 }

        h = Http(**self.http_options)
        return h.request( "{}?{}".format(self.codeEndpoint, urllib.urlencode(params)), method="POST", body = {} )

    def getTokenProfile(self, content):
        h = Http(**self.http_options)
        result = simplejson.loads(content)
        access_token = result['access_token']
        return access_token, h.request('{}?{}'.format(self.profileEndpoint, urllib.urlencode({'access_token':access_token})), method="GET")

    def getProfileFromData(self, token, data):
        """
        {
            "name" : "Martin Peschke",
            "id" : 314708,
            "bio" : "Founder SeriousCorp OFW",
            "follower_count" : 0,
            "angellist_url" : "https://angel.co/martin-peschke",
            "image" : "https://s3.amazonaws.com/photos.angel.co/users/314708-medium_jpg?1370246967",
            "email" : "martin@hackandcraft.com",
            "blog_url" : null,
            "online_bio_url" : null,
            "twitter_url" : null,
            "facebook_url" : null,
            "linkedin_url" : "http://www.linkedin.com/in/martinpeschke",
            "aboutme_url" : null,
            "github_url" : null,
            "dribbble_url" : null,
            "behance_url" : null,
            "what_ive_built" : null,
            "locations" : [],
            "roles" : [],
            "skills" : [],
            "investor" : false,
            "scopes" : ["email", "message", "dealflow"]
        }
        """
        profile = simplejson.loads(data)
        return {
                'type': SOCIAL_NETWORK_TYPES_REVERSE[self.type]
                , 'id':profile['id']
                , 'accessToken':token
                , 'picture': profile.get('image', "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm")
                , 'email': profile['email']
                , 'name': profile['name']
            }

    def getProfile(self, request):
        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice()
            else:
                return None
        resp, content = self.getAuthCode(request)
        if resp.status == 500:
            raise SocialNetworkException()
        if resp.status != 200:
            result = simplejson.loads(content)
            return None
        else:
            token, (resp, data) = self.getTokenProfile(content)
            if resp.status == 500:
                raise SocialNetworkException()
            if resp.status != 200:
                result = simplejson.loads(data)
                return None
            else:
                return self.getProfileFromData(token, data)

    def unwrapCompanies(self, data):
        result = simplejson.loads(data)
        return map(CompanyRoleModel.wrap, result['startup_roles'])

    def getCompaniesData(self, user_id, token):
        h = Http(**self.http_options)
        resp, data = h.request('{}?{}'.format(self.companiesEndpoint, urllib.urlencode({'access_token':token, 'v':'1', 'user_id':user_id})), method="GET")
        if resp.status == 500:
            raise SocialNetworkException()
        if resp.status != 200:
            return None
        else:
            return self.unwrapCompanies(data)

    def getCompanyData(self, company_id, token):
        h = Http(**self.http_options)
        resp, data = h.request(self.companyEndpoint.format(company_id = company_id), method="GET")
        if resp.status == 500:
            raise SocialNetworkException()
        if resp.status != 200:
            return None
        else:
            return CompanyModel.wrap(simplejson.loads(data))