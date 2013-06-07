import base64, logging
from symbol import decorator
from hnc.apiclient.backend import DBNotification, DBException
from hnc.forms.formfields import BaseForm
from hnc.forms.handlers import FormHandler
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from ufostart.website.apps.models.auth import SocialNetworkProfileModel
from ufostart.website.apps.models.procs import RefreshAccessTokenProc, SocialConnectProc
from ufostart.website.apps.social import AdditionalInformationRequired


log = logging.getLogger(__name__)



def login_user(context, request, profile):
    params = {'Profile': [profile]}
    if not request.root.user.isAnon():
        params['token'] = request.root.user.token
    try:
        user = SocialConnectProc(request, params)
    except DBNotification, e:
        log.error("UNHANDLED DB MESSAGE: %s", e.message)
        return None
    else:
        return user.toJSON()


def social_login(with_login = False):
    def social_login_real(fn):
        def social_login_inner(context, request):
            network = request.matchdict['network']
            networkSettings = context.settings.networks.get(network)

            #execute social handshakes for oauth1 and 2
            profile = networkSettings.getSocialProfile(
                            request
                            , request.fwd_url("website_index")
                        )

            if isinstance(profile, SocialNetworkProfileModel):

                if with_login:
                    login_user(context, request, profile)

                # execute result function
                return fn(context, request, profile)

            else:
                return profile
        return social_login_inner
    return social_login_real




@social_login(with_login  = True)
def login(context, request, profile):
    route, args, kwargs = request.root.getPostLoginUrlParams()
    request.fwd(route, *args, **kwargs)



