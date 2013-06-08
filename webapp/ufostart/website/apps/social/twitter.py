import logging
import urllib
from urlparse import parse_qsl
from hnc.forms.formfields import BaseForm, REQUIRED, EmailField
from hnc.forms.handlers import FormHandler
from hnc.tools.oauth import Consumer, Client, Token
from pyramid.decorator import reify
from pyramid.renderers import render_to_response
from pyramid.view import view_config, view_defaults
import simplejson
from ufostart.website.apps.social import SocialSettings, SocialNetworkException, assemble_profile_procs, SocialNetworkProfileModel, SocialLoginSuccessful

log = logging.getLogger(__name__)






class SocialResource(SocialSettings):
    getCodeEndpoint = "https://api.twitter.com/oauth/request_token"
    codeEndpoint = "https://api.twitter.com/oauth/authorize"
    tokenEndpoint = "https://api.twitter.com/oauth/access_token"
    profileEndpoint = "https://api.twitter.com/1.1/users/show.json"
    emailTemplate = 'ufostart:website/templates/auth/twitter_email.html'


    def verifyUser(self, request, profile):
        return False


    @reify
    def consumer(self):
        return Consumer(self.appid, self.appsecret)


@view_config(context = SocialResource)
def redirect_view(context, request):
    params = {'oauth_callback':request.rld_url(traverse=[context.network, 'cb'], with_query = False)}

    client = Client(context.consumer)
    resp, data = client.request(context.getCodeEndpoint, method="POST",body=urllib.urlencode(params))
    result = dict(parse_qsl(data))
    token = result.get("oauth_token")
    secret = result.get("oauth_token_secret")

    if resp.status != 200 or not (token and secret):
        raise SocialNetworkException(data)
    request.session['SOCIAL_TOKEN_{}'.format(context.network)] = Token(token, secret)

    params = urllib.urlencode({'oauth_token': token})
    request.fwd_raw("{}?{}".format(context.codeEndpoint, params))


def token_func(context, request):
    tokenSecret = request.session.pop('SOCIAL_TOKEN_{}'.format(context.network))
    verifier = request.params.get('oauth_verifier')
    if not (tokenSecret and verifier):
        raise SocialNetworkException('PARAM missing tokenSecret or verifier')
    tokenSecret.set_verifier(verifier)

    client = Client(context.consumer, tokenSecret)
    return client.request(context.tokenEndpoint, method="POST", headers={'Accept':'application/json'})


def profile_func(content, context, request):
    result = dict(parse_qsl(content))

    token = result.get('oauth_token')
    secret  = result.get('oauth_token_secret')
    user_id = result.get('user_id')
    if not (token and secret and user_id):
        raise SocialNetworkException('PARAM missing from {}'.format(result))

    token = Token(token, secret)
    client = Client(context.consumer, token, **context.http_options)
    return token, client.request('{}?user_id={}'.format(context.profileEndpoint, user_id), method="GET")


def parse_profile_func(token, data, context, request):
    profile = simplejson.loads(data)

    return SocialNetworkProfileModel(
        network = context.network
        , id = profile['id']
        , accessToken = token.key
        , secret = token.secret
        , picture = profile['profile_image_url_https']
        , name = profile['name']
        , original = profile
    )


get_profile = assemble_profile_procs(token_func, profile_func, parse_profile_func)

@view_config(context = SocialResource, name="cb")
def callback_view(context, request):
    profile = get_profile(context, request)
    isKnown = context.verifyUser(request, profile)
    if isKnown:
        raise SocialLoginSuccessful(profile)
    else:
        request.session['SOCIAL_BACKUP_{}'.format(context.network)] = profile
        request.rld(traverse=[context.network, 'email'], with_query = False)



class TwitterEmailFormForm(BaseForm):
    id="TwitterEmailForm"
    label = ""
    fields=[EmailField('email', 'Email', REQUIRED)]
    @classmethod
    def on_success(cls, request, values):
        return {'success':True, 'redirect': request.rld_url()}

@view_defaults(context = SocialResource, name="email")
class TwitterEmailFormHandler(FormHandler):
    form = TwitterEmailFormForm

    @view_config(request_method = 'POST', xhr=False)
    def POST(self):
        return super(TwitterEmailFormHandler, self).POST()

    @view_config(request_method = 'GET')
    def GET(self):
        result = super(TwitterEmailFormHandler, self).GET()
        result['view'] = self
        return render_to_response(self.context.emailTemplate, result, self.request)

    @view_config(request_method = 'POST', xhr=True, renderer='json')
    def ajax(self):
        return super(TwitterEmailFormHandler, self).ajax()