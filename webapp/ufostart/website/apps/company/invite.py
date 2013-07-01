from hnc.apiclient import TextField
from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, EmailField, REQUIRED, HiddenField, ChoiceField, TextareaField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage, GenericErrorMessage
from pyramid.httpexceptions import HTTPFound
from ufostart.models.tasks import NamedModel, RoleModel
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.forms.controls import SanitizedHtmlField
from ufostart.website.apps.models.procs import InviteToCompanyProc, GetInviteDetailsProc, AcceptInviteProc, RefreshProfileProc, AddUpdateCompanyProc


class BaseInviteForm(BaseForm):
        id="InviteCompany"

        @classmethod
        def on_success(cls, request, values):
            user = request.root.user
            company = request.context.company

            values['invitorToken'] = user.token
            values['invitorName'] = user.name
            values['companySlug'] = company.slug

            InviteToCompanyProc(request, {'Invite': [values]})

            request.session.flash(GenericSuccessMessage("You successfully invited {name} to your company!".format(**values)), "generic_messages")
            return {'success':True, 'redirect': request.resource_url(request.context)}

def InviteMentorForm(role_):
    class InviteForm(BaseInviteForm):
        role = role_
        fields = [
            StringField("name", "Name", REQUIRED)
            , EmailField("email", "email address", REQUIRED)
            , HiddenField("role")
        ]
    return InviteForm

ROLES = [RoleModel(key = "FOUNDER", label = "Founder"), RoleModel(key = "TEAM_MEMBER", label = "Team Member")]



class InviteTeamForm(BaseInviteForm):
    fields = [
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "email address", REQUIRED)
        , ChoiceField("role", "Invitee is", lambda x: ROLES)
    ]
class PostUpdateForm(BaseForm):
    id = "PostUpdate"
    fields = [SanitizedHtmlField("text", None, REQUIRED)]
    @classmethod
    def on_success(cls, request, values):
        AddUpdateCompanyProc(request, {'token': request.context.company.token, 'update': {'userToken': request.root.user.token, 'text': values['text']}})
        return {'success': True, 'redirect': request.resource_url(request.context)}

class CompanyIndexHandler(FormHandler):
    forms = [InviteTeamForm, PostUpdateForm]

    def pre_fill_values(self, request, result):
        company = request.context.company
        result['company'] = company
        return super(CompanyIndexHandler, self).pre_fill_values(request, result)



class AddMentorHandler(FormHandler):
    form = InviteMentorForm('MENTOR')
    def pre_fill_values(self, request, result):
        company = self.context.company
        result['company'] = company
        return super(AddMentorHandler, self).pre_fill_values(request, result)





def showInfo(context, request):
    return {'invite': context.invite}

def confirm(context, request):
    AcceptInviteProc(request, {'inviteToken':context.__name__, 'userToken': request.root.user.token})
    RefreshProfileProc(request, {'token': request.root.user.token})
    raise HTTPFound(request.root.company_url(context.invite.companySlug))

