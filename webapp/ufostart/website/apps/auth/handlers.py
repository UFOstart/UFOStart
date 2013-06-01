from hnc.apiclient.backend import DBNotification
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericErrorMessage
from pyramid.httpexceptions import HTTPFound
from ufostart.website.apps.auth.forms import LoginForm, SignupForm, PasswordForgotForm, PasswordResetForm, DecisionForm
from ufostart.website.apps.models.auth import CheckEmailExistsProc, PasswordTokenVerifyProc




class DecisionHandler(FormHandler):
    form = DecisionForm




################### NOTE: DEPRECATED


def require_li(context, request):
    return {}



def join_checkemail(context, request):
    return True
    # TODO: make work, pending API
    try:
        CheckEmailExistsProc(request, {"email": request.params.get('signup.email')})
    except DBNotification, e:
        return "Email already taken"
    else:
        return True

def logout(context, request):
    context.logout()
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd("website_index")


class SignupHandler(FormHandler):
    forms = [LoginForm, SignupForm]

class WebsitePasswordForgotHandler(FormHandler):
    form = PasswordForgotForm

class PasswordResetHandler(FormHandler):
    form = PasswordResetForm
    def is_valid(self):
        request = self.request
        try:
            user = PasswordTokenVerifyProc(request, request.matchdict)
            self.context.user = user
        except DBNotification, e:
            request.session.flash(GenericErrorMessage("Invalid Link. Please check the link or request a new password forgot email."), "generic_messages")
            request.fwd("website_index")
        else:
            return True

    def GET(self):
        if self.is_valid():
            return super(PasswordResetHandler, self).GET()

    def POST(self):
        if self.is_valid():
            return super(PasswordResetHandler, self).POST()


    def ajax(self):
        try:
            self.is_valid()
            result = self.validate_json()
            return result
        except HTTPFound, e: # success case
            return {'redirect': e.location, "errorMessage": ",".join(self.request.session.pop_flash())}