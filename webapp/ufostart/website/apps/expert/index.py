from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, REQUIRED, TextareaField, ConfigChoiceField, ChoiceField, NullConfigModel
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from ufostart.models.tasks import TASK_CATEGORIES
from ufostart.website.apps.models.procs import CreateNeedProc

__author__ = 'Martin'


def index(context, request):
    return {}


def optionGetter(request):
    return [NullConfigModel()] + TASK_CATEGORIES


class TaskCreateForm(BaseForm):
    id="TaskCreate"
    label = ""
    fields=[
        StringField('name', "Need Name", REQUIRED)
        , TextareaField("description", "Description", REQUIRED)
        , ChoiceField("category", "Need Type", optionGetter, REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        try:
            CreateNeedProc(request, values)
        except DBNotification, e:
            if e.message == 'ALREADY_EXISTS':
                return {'success':False, 'errors': {'name': "Already used, please choose another name!"}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage("Need created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("website_expert_dashboard")}

class TaskCreateHandler(FormHandler):
    form = TaskCreateForm