from pyramid.httpexceptions import HTTPFound
from ufostart.website.apps.models.procs import PublishRoundProc, AskForApprovalProc


def index(context, request):
    company = context.company
    if not company:
        request.fwd("website_index")
    return {'company': company, 'currentRound':company.currentRound}


def publish_round(context, request):
    wf = context.round.Workflow
    if wf and wf.canPublish():
        PublishRoundProc(request, {'token': context.round.token})
    raise HTTPFound(request.resource_url(context))

def ask_for_approval(context, request):
    wf = context.round.Workflow
    if wf and wf.canAskForApproval():
        AskForApprovalProc(request, {'token': context.round.token})
    raise HTTPFound(request.resource_url(context))
