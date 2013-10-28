import logging
import re
from hnc.apiclient.backend import DBNotification, DBException
from hnc.forms.formfields import REQUIRED, HtmlAttrs, IntField, ChoiceField
from hnc.forms.handlers import FormHandler
from hnc.forms.layout import BS3_NCOL
from hnc.forms.messages import GenericErrorMessage
from pyramid.response import Response
from ufostart.handlers.forms.controls import UniqueNameField, TagSearchField
from ufostart.lib.baseviews import BaseForm
from ufostart.models.auth import SocialNetworkProfileModel, SOCIAL_NETWORK_TYPES_REVERSE, SOCIAL_NETWORK_TYPES
from ufostart.models.procs import LinkedinSignupProc, UsernameAvailableProc, SetUserInfoProc
from ufostart.models.tasks import NamedModel

log = logging.getLogger(__name__)


uname_regex = re.compile('^[0-9a-z_.-]+$')
_= lambda s:s

RESERVEDS = []


def isavailable(context, request):
    try:
        username = request.json_body['name']
    except:
        username = ''.join(request.params.values())

    if not uname_regex.match(username):
        return "Name should only contain numbers, lowercase characters, underscores and hyphens"
    elif username in RESERVEDS:
        return "Name already taken"
    else:
        try:
            UsernameAvailableProc(request, {'slug': username})
        except (DBNotification, DBException), e:
            return "Name already taken"
        else:
            return True


group_classes = UniqueNameField.group_classes + " input-larger"

class UserNameForm(BaseForm):
    id="UserName"
    fields=[
        UniqueNameField("username", _("SignupPage.Username.Label:Choose your username"), input_classes='input-lg', group_classes = group_classes, thing_name = 'username')
    ]
    @classmethod
    def on_success(cls, request, values):
        username = values['username']
        furl = request.root.signup_url(username, 'linkedin')
        return {'success':True, 'redirect': furl}

class UserNameHandler(FormHandler):
    form = UserNameForm

    def pre_fill_values(self, request, result):
        if not request.context.user.isAnon():
            request.fwd(request.root)
        if request.context.has_username:
            result['values'][self.form.id]['username'] = request.context.__name__
        return super(UserNameHandler, self).pre_fill_values(request, result)


def signup_user(context, request, profile):
    if isinstance(profile, SocialNetworkProfileModel):
        profile = profile.unwrap(sparse = True)
        if profile.get('network') and not profile.get('type'):
            profile['type'] = SOCIAL_NETWORK_TYPES_REVERSE[profile['network']]
        elif not profile.get('network') and profile.get('type'):
            profile['network'] = SOCIAL_NETWORK_TYPES[profile['type']]

    params = {'Profile': [profile], 'slug': context.__name__}
    if not request.root.user.isAnon():
        params['token'] = request.root.user.token
    return LinkedinSignupProc(request, params)



def login_success(exc, request):
    ctxt = request.context.__parent__
    try:
        user = signup_user(ctxt, request, exc.profile)
    except (DBNotification, DBException), e:
        if e.message == 'USER_ALREADY_REGISTERED':
            request.session.flash(GenericErrorMessage("This Linkedin user is already registered. Please click the Login with Linkedin button."), "generic_messages")
        elif e.message == 'USER_SLUG_TAKEN':
            request.session.flash(GenericErrorMessage("This username is already registered. Please choose another one."), "generic_messages")
        else:
            request.session.flash(GenericErrorMessage(e.message), "generic_messages")
        return Response("Resource Found!", 302, headerlist = [('location', request.fwd_url(ctxt))])
    else:
        return Response("Resource Found!", 302, headerlist = [('location', request.root.signup_url('getstarted'))])


def login_failure(exc, request):
    ctxt = request.context.__parent__
    request.session.flash(GenericErrorMessage(exc.message), "generic_messages")
    return Response("Resource Found!", 302, headerlist = [('location', request.fwd_url(ctxt))])


#=================================================== ROLE SELECT =======================================================

def role_select_on_success(cls, request, values):
    user = request.context.user
    values['token'] = user.token
    values['Roles'] = [{'name':role} for role in cls.ROLES]
    SetUserInfoProc(request, values)
    return {'success':True, 'redirect': request.root.profile_url(user.slug)}

class ExpertForm(BaseForm):
    id="expert"
    ROLES = ['EXPERT']
    fields=[
        TagSearchField("Skills", "Add your Skills", '/web/tag/search', 'Tags', attrs = HtmlAttrs(placeholder = "Find Skills"))
    ]
    on_success = classmethod(role_select_on_success)

class InvestorForm(BaseForm):
    id="investor"
    ROLES = ['INVESTOR']
    fields=[
        BS3_NCOL(
            IntField("investmentAmount", "Enter Annual Investment Amount")
            , ChoiceField("currency", "Investment Currency", optionGetter=lambda s: [NamedModel(name = 'EUR'), NamedModel(name = 'USD')], attrs = REQUIRED)
        )
    ]
    on_success = classmethod(role_select_on_success)

class FounderForm(BaseForm):
    id="founder"
    ROLES = ['FOUNDER']
    fields=[]
    @classmethod
    def on_success(cls, request, values):
        user = request.context.user
        values['token'] = user.token
        values['Roles'] = [{'name':role} for role in cls.ROLES]
        SetUserInfoProc(request, values)
        return {'success':True, 'redirect': request.root.template_select_url}

class UserRoleHandler(FormHandler):
    def pre_fill_values(self, request, result):
        result['values'][ExpertForm.id] = {"Skills" : [m.unwrap() for m in request.context.user.Skills]}
        return super(UserRoleHandler, self).pre_fill_values(request, result)

    @property
    def site_title(self):
        return ['What are you?', self.request.globals.project_name]
    forms = [ExpertForm, InvestorForm, FounderForm]