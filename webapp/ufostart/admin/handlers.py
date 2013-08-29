from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import TextareaField, REQUIRED, StringField, HtmlAttrs, ChoiceField, URLField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from ufostart.lib.baseviews import BaseForm
from ufostart.apps.forms.controls import TagSearchField, PictureUploadField
from ufostart.models.procs import AdminCreateNeedProc, AdminEditNeedProc, AdminServiceCreateProc, AdminServiceEditProc
from ufostart.models.tasks import TASK_CATEGORIES


def index(context, request): return {}



class TaskCreateForm(BaseForm):
    label = "Create Task"
    fields = [
        StringField('name', "Title", REQUIRED)
        , ChoiceField("category", "Category", lambda s: TASK_CATEGORIES)
        , TextareaField("description", "Description", REQUIRED, input_classes='x-high')
        , TagSearchField("Tags", "Related Tags", '/web/tag/search', 'Tags', attrs = HtmlAttrs(required=True, data_required_min = 3, placeholder = "Add Tags"))
        , TagSearchField("Services", "Related Web Services", '/web/service/search', 'Services', attrs = HtmlAttrs(required=True, data_required_min = 3, placeholder = "Add Services"))
    ]

    @classmethod
    def on_success(cls, request, values):
        try:
            need = AdminCreateNeedProc(request, values)
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This task already exists, please change the name to a unique name."}}
            else:
                raise e
        request.session.flash(GenericSuccessMessage("Task created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class TaskCreateHandler(FormHandler):
    form = TaskCreateForm



class TaskEditForm(TaskCreateForm):
    label = "Edit Task"
    @classmethod
    def on_success(cls, request, values):
        values['key'] = request.context.task.key
        need = AdminEditNeedProc(request, values)
        request.session.flash(GenericSuccessMessage("Task updated successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context.__parent__)}


class TaskEditHandler(FormHandler):
    form = TaskEditForm
    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = request.context.task.unwrap()
        return super(TaskEditHandler, self).pre_fill_values(request, result)







class ServiceCreateForm(BaseForm):
    label = "Create Service"
    fields = [
        StringField('name', "Name", REQUIRED)
        , URLField('url', "website", REQUIRED)
        , PictureUploadField("logo", "Logo")
    ]

    @classmethod
    def on_success(cls, request, values):
        try:
            need = AdminServiceCreateProc(request, values)
        except DBNotification, e:
            if e.message == 'Service_Already_Exists':
                return {'success':False, 'errors': {'name': "This service already exists, please change the name to a unique name."}}
            else:
                raise e
        request.session.flash(GenericSuccessMessage("Service created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class ServiceCreateHandler(FormHandler):
    form = TaskCreateForm




class ServiceEditForm(ServiceCreateForm):
    label = "Edit Service"
    fields = [
        URLField('url', "website", REQUIRED)
        , PictureUploadField("logo", "Logo")
    ]
    @classmethod
    def on_success(cls, request, values):
        values['name'] = request.context.service.name
        need = AdminServiceEditProc(request, values)
        request.session.flash(GenericSuccessMessage("Service updated successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context.__parent__)}


class ServiceEditHandler(FormHandler):
    form = ServiceEditForm
    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = request.context.service.unwrap()
        return super(ServiceEditHandler, self).pre_fill_values(request, result)


