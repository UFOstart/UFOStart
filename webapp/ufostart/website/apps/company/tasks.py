from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm
from hnc.forms.handlers import FormHandler
from pyramid.decorator import reify
from ufostart.lib.tools import group_by_n
from ufostart.models.tasks import TASK_CATEGORIES
from ufostart.website.apps.models.procs import GetRoundProc, SetCompanyTemplateProc, GetCompanyProc, CreateRoundProc, GetAllCompanyTemplatesProc, GetTemplateDetailsProc, GetAllNeedsProc, SetRoundTasksProc


def needs_template_select(context, request):
    templates = GetAllCompanyTemplatesProc(request)
    return {'templates': group_by_n(templates)}


class TasksForm(BaseForm):
    fields = []

    @classmethod
    def on_success(cls, request, values):
        company = request.root.company
        if not company or not company.Round: request.fwd("website_index")
        needs = [values['needKey']] if isinstance(values['needKey'], basestring) else values['needKey']
        values = {"token": company.Round.token, "Needs": [{ "name": k } for k in needs]}
        try:
            SetRoundTasksProc(request, values)
        except DBNotification, e:
            raise e
        else:
            return {'success': True, 'redirect': request.fwd_url("website_company_round_view", slug = request.matchdict['slug'], _query = [('s', '1')])}

class TasksHandler(FormHandler):
    form = TasksForm
    def pre_fill_values(self, request, result):
        result['CATEGORIES'] = TASK_CATEGORIES
        return super(TasksHandler, self).pre_fill_values(request, result)

    @reify
    def template(self):
        request = self.request
        templateName = request.matchdict['template']
        return GetTemplateDetailsProc(request, {'name': templateName})

    @reify
    def categorizedTasks(self):
        request = self.request
        result = {}
        for need in self.template.Need:
            map = result.setdefault(need.category, [])
            need._inUse = True
            map.append(need)
        return result


    @reify
    def categorizedAllTasks(self):
        usedNeeds = {t.name:True for t in self.template.Need}
        request = self.request
        result = {}
        allNeeds = GetAllNeedsProc(request)
        for need in allNeeds:
            map = result.setdefault(need.category, [])
            need._inUse =  need.name in usedNeeds
            map.append(need)
        return result




def index(context, request):
    currentRound = context.company.getCurrentRound()
    return {'currentRound': currentRound}


def need_library(context, request):
        templates = GetAllCompanyTemplatesProc(request)
        templates = group_by_n(templates)
        return {'templates': templates}