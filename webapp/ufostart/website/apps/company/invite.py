from hnc.forms.formfields import BaseForm, StringField, EmailField, REQUIRED, HiddenField, ChoiceField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage, GenericErrorMessage
from pyramid.httpexceptions import HTTPFound
from ufostart.lib import html
from ufostart.models.tasks import RoleModel
from ufostart.website.apps.forms.controls import SanitizedHtmlField
from ufostart.website.apps.models.procs import InviteToCompanyProc, AcceptInviteProc, RefreshProfileProc, AddUpdateCompanyProc, GetTopMentorsProc, GetProfileProc


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


class AddMentorHandler(FormHandler):
    form = InviteMentorForm('MENTOR')

    def pre_fill_values(self, request, result):
        result['mentors'] = GetTopMentorsProc(request).User
        return super(AddMentorHandler, self).pre_fill_values(request, result)

def add_top_mentor(context, request):
    mentorToken = request.params.get('m')
    mentor  = GetProfileProc(request, {'token': mentorToken})
    if not mentor:
        request.session.flash(GenericErrorMessage("Not a valid mentor!"), "generic_messages")
        raise HTTPFound(request.resource_url(request.context, 'mentor'))

    user = request.root.user
    company = request.context.company

    values = {'invitorToken': user.token, 'invitorName': user.name, 'companySlug':  company.slug, 'userToken': mentorToken, 'role':'MENTOR', 'email':mentor.email, 'name':mentor.name}
    InviteToCompanyProc(request, {'Invite': [values]})

    request.session.flash(GenericSuccessMessage("You successfully invited {name} to your company!".format(**values)), "generic_messages")
    raise HTTPFound(request.resource_url(request.context))

def showInfo(context, request):
    return {'invite': context.invite}

def confirm(context, request):
    AcceptInviteProc(request, {'inviteToken':context.__name__, 'userToken': request.root.user.token})
    RefreshProfileProc(request, {'token': request.root.user.token})
    raise HTTPFound(request.root.company_url(context.invite.companySlug))

def reject(context, request):
    raise HTTPFound(request.root.company_url(context.invite.companySlug))

