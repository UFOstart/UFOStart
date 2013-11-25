from hnc.apiclient.backend import DBNotification, DBException
from hnc.forms.formfields import TextareaField, REQUIRED, StringField, HtmlAttrs, ChoiceField, URLField, CheckboxField, CheckboxPostField, Field, MultipleFormField
from hnc.forms.handlers import FormHandler
from hnc.forms.layout import BS3_NCOL, Sequence
from hnc.forms.messages import GenericSuccessMessage
from hnc.tools.tools import deep_get
from ufostart.lib.baseviews import BaseForm
from ufostart.handlers.forms.controls import TagSearchField, PictureUploadField
from ufostart.models.procs import AdminNeedCreateProc, AdminNeedEditProc, AdminServiceCreateProc, AdminServiceEditProc, AdminTemplatesEditProc, AdminTemplatesCreateProc, AdminNeedAllProc, SetStaticContentProc, AdminPageEditProc, AdminPageCreateProc
from ufostart.models.tasks import TASK_CATEGORIES


def index(context, request): return {}



class TaskCreateForm(BaseForm):
    label = "Create Task"
    fields = [
        StringField('name', "Title", REQUIRED)
        , ChoiceField("category", "Category", lambda s: TASK_CATEGORIES)
        , TextareaField("summary", "Summary", REQUIRED, input_classes='x-high')
        , TagSearchField("Tags", "Related Tags", '/web/tag/search', 'Tags', attrs = HtmlAttrs(required=True, data_required_min = 3, placeholder = "Add Tags"))
        , TagSearchField("Services", "Related Web Services", '/web/service/search', 'Services', attrs = HtmlAttrs(required=True, data_required_min = 3, placeholder = "Add Services"))
    ]

    @classmethod
    def on_success(cls, request, values):
        try:
            need = AdminNeedCreateProc(request, values)
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This task already exists, please change the name to a unique name."}}
            else:
                return {'success':False, 'message':e.message}
        except DBException, e:
            return {'success':False, 'message':e.message}
        request.session.flash(GenericSuccessMessage("Task created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class TaskCreateHandler(FormHandler):
    form = TaskCreateForm



class TaskEditForm(TaskCreateForm):
    label = "Edit Task"
    @classmethod
    def on_success(cls, request, values):
        values['key'] = request.context.task.key
        try:
            need = AdminNeedEditProc(request, values)
        except (DBNotification, DBException), e:
            return {'success':False, 'message':e.message}
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
        , URLField('url', "Website", REQUIRED)
        , PictureUploadField("logo", "Logo", picWidth=100, picHeight=100)
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
    form = ServiceCreateForm




class ServiceEditForm(ServiceCreateForm):
    label = "Edit Service"
    fields = [
        URLField('url', "website", REQUIRED)
        , PictureUploadField("logo", "Logo", picWidth=100, picHeight=100)
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




class NeedSelector(Field):
    template = "ufostart:templates/admin/controls/needselect.html"
    def allNeeds(self, request):
        return AdminNeedAllProc(request)
    def getValidator(self, request):
        return {}
    def getValues(self, name, request, values, errors, view):
        return {'value': filter(None, [v.get('name') for v in values.get('Need', [])])}



class TemplateCreateForm(BaseForm):
    label = "Create Template"
    fields = [
        BS3_NCOL(
            Sequence(
                StringField('name', "Name", REQUIRED)
                , TextareaField('description', "Description", REQUIRED, input_classes='x-high')
                , PictureUploadField("picture", "Picture", picWidth=277, picHeight=230)
                , CheckboxPostField('active', "Active?")
            )
            , NeedSelector('Need', "Task List")
        )
    ]

    @classmethod
    def on_success(cls, request, values):
        values['Need'] = [{'name':n} for n in values.pop('Need', [])]
        try:
            need = AdminTemplatesCreateProc(request, values)
        except DBNotification, e:
            if e.message == 'Template_Already_Exists':
                return {'success':False, 'errors': {'name': "This template already exists, please change the name to a unique name."}}
            else:
                raise e
        request.session.flash(GenericSuccessMessage("Template created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class TemplateCreateHandler(FormHandler):
    form = TemplateCreateForm




class TemplateEditForm(TemplateCreateForm):
    label = "Edit Template"
    @classmethod
    def on_success(cls, request, values):
        values['key'] = request.context.__name__
        values['Need'] = [{'name':n} for n in values.pop('Need', [])]
        need = AdminTemplatesEditProc(request, values)
        request.session.flash(GenericSuccessMessage("Template updated successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context.__parent__)}

class TemplateEditHandler(FormHandler):
    form = TemplateEditForm
    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = request.context.template.unwrap() or {}
        return super(TemplateEditHandler, self).pre_fill_values(request, result)





class PageCreateForm(BaseForm):
    label = "Create Page"
    fields = [
        StringField('url', "URL", REQUIRED)
        , StringField('title', "title", REQUIRED)
        , StringField('metaKeywords', "Meta Keywords")
        , StringField('metaDescription', "Meta Description")
        , TextareaField('content', "Content", input_classes='x-high')
    ]

    @classmethod
    def on_success(cls, request, values):
        values['Need'] = [{'name':n} for n in values.pop('Need', [])]
        try:
            need = AdminPageCreateProc(request, values)
        except DBNotification, e:
            if e.message == 'Page_Already_Exists':
                return {'success':False, 'errors': {'name': "This Page already exists, please change the name to a unique name."}}
            else:
                raise e
        request.session.flash(GenericSuccessMessage("Page created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class PageCreateHandler(FormHandler):
    form = PageCreateForm



class PageEditForm(PageCreateForm):
    label = "Edit Page"
    @classmethod
    def on_success(cls, request, values):
        values['key'] = request.context.__name__
        values['Need'] = [{'name':n} for n in values.pop('Need', [])]
        need = AdminPageEditProc(request, values)
        request.session.flash(GenericSuccessMessage("Page updated successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context.__parent__)}

class PageEditHandler(FormHandler):
    form = PageEditForm
    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = request.context.page.unwrap() or {}
        return super(PageEditHandler, self).pre_fill_values(request, result)


