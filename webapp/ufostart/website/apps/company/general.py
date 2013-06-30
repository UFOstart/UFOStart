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