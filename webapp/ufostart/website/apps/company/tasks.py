from ufostart.lib.tools import group_by_n
from ufostart.website.apps.models.procs import GetAllCompanyTemplatesProc


def index(context, request):
    currentRound = context.company.getCurrentRound()
    return {'currentRound': currentRound}

def need_library(context, request):
    templates = GetAllCompanyTemplatesProc(request)
    templates = group_by_n(templates)
    return {'templates': templates}