from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm
from hnc.forms.handlers import FormHandler
from pyramid.decorator import reify
from ufostart.lib.tools import group_by_n
from ufostart.models.tasks import TASK_CATEGORIES
from ufostart.website.apps.models.procs import GetRoundProc, SetCompanyTemplateProc, GetCompanyProc, CreateRoundProc, GetAllCompanyTemplatesProc, GetTemplateDetailsProc, GetAllNeedsProc, SetRoundTasksProc


def index(context, request):
    currentRound = context.company.getCurrentRound()
    return {'currentRound': currentRound}


def need_library(context, request):
        templates = GetAllCompanyTemplatesProc(request)
        templates = group_by_n(templates)
        return {'templates': templates}