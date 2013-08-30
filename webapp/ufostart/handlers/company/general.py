from hnc.forms.formfields import StringField, EmailField, REQUIRED, HiddenField, ChoiceField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage, GenericErrorMessage
from pyramid.httpexceptions import HTTPFound
from ufostart.lib.baseviews import BaseForm

from ufostart.handlers.forms.controls import SanitizedHtmlField
from ufostart.models.tasks import ROLES
from ufostart.models.procs import InviteToCompanyProc, AcceptInviteProc, RefreshProfileProc, AddUpdateCompanyProc, GetTopMentorsProc, GetProfileProc, PublishRoundProc, AskForApprovalProc




def publish_round(context, request):
    wf = context.round.Workflow
    if wf and wf.canPublish():
        PublishRoundProc(request, {'token': context.round.token})
    raise HTTPFound(request.resource_url(context))

def reject_round(context, request):
    raise HTTPFound(request.resource_url(context))

def ask_for_approval(context, request):
    wf = context.round.Workflow
    if wf and wf.canAskForApproval():
        AskForApprovalProc(request, {'token': context.round.token})
    raise HTTPFound(request.resource_url(context))


class BaseInviteForm(BaseForm):
    id="InviteCompany"
    fields = [
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "Email address", REQUIRED)
    ]

    @classmethod
    def on_success(cls, request, values):
        user = request.root.user
        company = request.context.company

        values['invitorToken'] = user.token
        values['invitorName'] = user.name
        values['companySlug'] = company.slug

        InviteToCompanyProc(request, {'Invite': [values]})

        request.session.flash(GenericSuccessMessage(u"You successfully invited {name} to your company!".format(**values)), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class MentorInviteForm(BaseInviteForm):
    @classmethod
    def on_success(cls, request, values):
        values['role'] = 'MENTOR'
        return BaseInviteForm.on_success(request, values)


def get_roles(request): return ROLES
class InviteTeamForm(BaseInviteForm):
    fields = BaseInviteForm.fields + [ChoiceField("role", "Invitee is", get_roles)]




class RoundDashboardHandler(FormHandler):
    form = InviteTeamForm


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
    form = MentorInviteForm

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

    request.session.flash(GenericSuccessMessage(u"You successfully invited {name} to your company!".format(**values)), "generic_messages")
    raise HTTPFound(request.resource_url(request.context))


def invite_landing(context, request):
    return {'invite': context.invite}

def confirm(context, request):
    AcceptInviteProc(request, {'inviteToken':context.__name__, 'userToken': request.root.user.token})
    RefreshProfileProc(request, {'token': request.root.user.token})
    raise HTTPFound(request.root.round_url(context.invite.companySlug, '1'))

def reject(context, request):
    raise HTTPFound(request.root.round_url(context.invite.companySlug, '1'))

