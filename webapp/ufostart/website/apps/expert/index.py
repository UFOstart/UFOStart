from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, REQUIRED, TextareaField, ConfigChoiceField, ChoiceField, NullConfigModel
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from ufostart.models.tasks import TASK_CATEGORIES
from ufostart.website.apps.models.procs import CreateNeedProc

__author__ = 'Martin'


def index(context, request):
    return {}

