from collections import namedtuple
import logging, simplejson
from hnc.forms.messages import GenericErrorMessage

log = logging.getLogger(__name__)

class SocialNotice(Exception): pass
class UserRejectedNotice(SocialNotice): pass
class InvalidSignatureException(Exception):pass
class SocialNetworkException(Exception):pass
class CustomProcessException(Exception):pass


class AdditionalInformationRequired(Exception):
    def __init__(self, template, params):
        self.template = template
        self.params = params





class SocialSettings(object):
    http_options = {'disable_ssl_certificate_validation' : True}
    default_picture = "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    def __init__(self, type, appid, appsecret):
        self.type = type
        self.appid = appid
        self.appsecret = appsecret

    def toPublicJSON(self, stringify = True):
        result = {'appId':self.appid, 'connect' : True}
        return simplejson.dumps(result) if stringify else result

    def loginStart(self, request):
        """
        Called first, when user intends to login, should redirect user to 3rd party
        """
        raise NotImplementedError

    def getAuthCode(self, request):
        """
        when user comes back, this should exchange auth_code for token
        """
        raise NotImplementedError
    def getTokenProfile(self, content):
        """
        this parses the getAuthCode Result and should query basic user details, return plain string response
        """
        raise NotImplementedError
    def getProfileFromData(self, token, data, request):
        """
        should extract profile data from plain string response into common format
        """
        raise NotImplementedError

    def customCallback(self, request):
        """
        whenever a differing flow needs to be offered, this is the place to do it
        """
        raise NotImplementedError


    def profileCallback(self, request):
        if request.params.get("error"):
            if 'denied' in request.params.get("error"):
                raise UserRejectedNotice()
            else:
                return None
        resp, content = self.getAuthCode(request)
        if resp.status == 500:
            raise SocialNetworkException()
        if resp.status not in [200,201]:
            return None
        else:
            token, (resp, data) = self.getTokenProfile(content)
            if resp.status == 500:
                raise SocialNetworkException()
            if resp.status != 200:
                result = simplejson.loads(data)
                return None
            else:
                return self.getProfileFromData(token, data, request)

    # EXPOSED Functions

    def getSocialProfile(self, request, error_url):
        action = request.matchdict['action']
        if action == 'start':
            # this will redirect, per oauth to get the code
            try:
                self.loginStart(request)
            except SocialNetworkException, e:
                request.session.flash(GenericErrorMessage("{} login failed.".format(self.type.title())), "generic_messages")
                request.fwd_raw(error_url)
        elif action == 'cb':
            #after redirect, this will do some more API magic and return the social profile
            try:
                profile = self.profileCallback(request)
            except UserRejectedNotice, e:
                request.session.flash(GenericErrorMessage("You need to accept {} permissions to use {}.".format(self.type.title(), request.globals.project_name)), "generic_messages")
                request.fwd_raw(error_url)
            except SocialNetworkException, e:
                request.session.flash(GenericErrorMessage("{} login failed.".format(self.type.title())), "generic_messages")
                request.fwd_raw(error_url)
            else:
                if not profile:
                    request.session.flash(GenericErrorMessage("{} login failed. It seems the request expired. Please try again".format(self.type.title())), "generic_messages")
                    request.fwd_raw(error_url)
                else:
                    return profile
        else:
            try:
                return self.customCallback(request)
            except CustomProcessException, e:
                request.session.flash(GenericErrorMessage("{} login failed.".format(self.type.title())), "generic_messages")
                request.fwd_raw(error_url)