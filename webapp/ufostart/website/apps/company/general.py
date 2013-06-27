from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, REQUIRED, TextareaField, HORIZONTAL_GRID
from hnc.forms.handlers import FormHandler
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.models.procs import CreateCompanyProc, CreateRoundProc, PublishRoundProc, AskForApprovalProc


def index(context, request):
    company = context.company
    if not company:
        request.fwd("website_index")
    return {'company': company, 'currentRound':company.currentRound}

def create_round(context, request):
    company = context.company
    if not company.currentRound:
        round = CreateRoundProc(request, {'slug': company.slug})
    request.fwd("website_company", **context.urlArgs)


class SetupCompanyForm(BaseForm):
    id="SetupCompany"
    grid = HORIZONTAL_GRID
    label = ""
    fields=[
        StringField("name", "Name", REQUIRED)
        , TextareaField("description", "Description", input_classes="x-high")
    ]
    @classmethod
    def on_success(cls, request, values):
        data = {"token": request.root.user.token, "Company": values}
        try:
            user = CreateCompanyProc(request,  data)
            company = user.Company
        except DBNotification, e:
            if e.message == 'Company_Already_Exists':
                return {'success':False, 'errors': {'name': "Already used, please choose another name!"}}
            else:
                raise e

        return {'success':True, 'redirect': request.fwd_url("website_company_invite", slug = company.slug)}

class SetupCompanyHandler(FormHandler):
    form = SetupCompanyForm


@require_login('ufostart:website/templates/auth/login.html')
def publish_round(context, request):
    round = context.company.currentRound
    if not round:
        raise HTTPNotFound()
    wf = round.Workflow
    if not wf or not wf.canPublish():
        request.fwd("website_company", **context.urlArgs)
    else:
        PublishRoundProc(request, {'token': round.token})
        request.fwd("website_company", **context.urlArgs)

@require_login('ufostart:website/templates/auth/login.html')
def ask_for_approval(context, request):
    round = context.company.currentRound
    if not round:
        raise HTTPNotFound()
    wf = round.Workflow
    if not wf or not wf.canAskForApproval():
        request.fwd("website_company", **context.urlArgs)
    else:
        AskForApprovalProc(request, {'token': round.token})
        request.fwd("website_company", **context.urlArgs)