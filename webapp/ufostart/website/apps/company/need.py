from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, REQUIRED, TextareaField, IntField, HtmlAttrs, HORIZONTAL_GRID, DecimalField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from pyramid.httpexceptions import HTTPFound
from ufostart.website.apps.forms.controls import FileUploadField, TagSearchField
from ufostart.website.apps.models.company import NeedModel
from ufostart.website.apps.models.procs import CreateNeedProc, EditNeedProc, ApplyForNeedProc, ApproveApplicationProc


def index(context, request):
    return {'need': context.need}


def accept_application(context, request):
    ApproveApplicationProc(request, {'token': context.application.token})
    raise HTTPFound(request.resource_url(context.__parent__))



class ApplicationForm(BaseForm):
    id="Application"
    label = ""
    grid = HORIZONTAL_GRID
    fields=[StringField('message', 'Message', REQUIRED)]
    @classmethod
    def on_success(cls, request, values):
        ApplyForNeedProc(request, {'token':request.context.need.token, 'Application': {'User':{'token':request.root.user.token}, 'message':values['message']}})
        request.session.flash(GenericSuccessMessage("You have applied for this need successfully. One of the team members will contact you shortly."), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class ApplicationHandler(FormHandler):
    form = ApplicationForm



class NeedCreateForm(BaseForm):
    id="NeedCreate"
    label = ""
    fields = [
        FileUploadField("picture", 'Picture', group_classes='file-upload-control')
        , StringField('name', "Need Name", REQUIRED)
        , IntField('total', "Total value ($)", REQUIRED, input_classes='data-input value')
        , IntField('ratio', "of this Equity (%)", REQUIRED, input_classes='data-input ratio', max = 100)
        , DecimalField('cash', None)
        , DecimalField('equity', None)
        , TextareaField("customText", "Description", REQUIRED, input_classes='x-high')
        , TagSearchField("Tags", "Related Tags", '/web/tag/search', 'Tags', attrs = HtmlAttrs(required=True, data_required_min = 3, placeholder = "Add Tags"))
    ]
    @classmethod
    def on_success(cls, request, values):
        try:
            need = CreateNeedProc(request, {'Needs':[values], 'token': request.context.round.token})
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This need already exists, if you intend to create this need, please change its name to something less ambiguous!"}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage("Need created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context, need.slug)}

class NeedCreateHandler(FormHandler):
    form = NeedCreateForm

    def pre_fill_values(self, request, result):
        result['need'] = NeedModel()
        return super(NeedCreateHandler, self).pre_fill_values(request, result)


class NeedEditForm(BaseForm):
    id="NeedEdit"
    label = ""
    fields = [
        FileUploadField("picture", 'Picture', group_classes='file-upload-control')
        , StringField('name', "Need Name", REQUIRED)
        , IntField('total', "Total value ($)", REQUIRED, input_classes='data-input value')
        , IntField('ratio', "of this Equity (%)", REQUIRED, input_classes='data-input ratio', max = 100)
        , DecimalField('cash', None)
        , DecimalField('equity', None)
        , TextareaField("customText", "Description", REQUIRED, input_classes='x-high')
        , TagSearchField("Tags", "Related Tags", '/web/tag/search', 'Tags', attrs = HtmlAttrs(required=True, data_required_min = 3, placeholder = "Add Tags"))
    ]

    @classmethod
    def on_success(cls, request, values):
        values['token'] = request.context.need.token

        try:
            round = EditNeedProc(request, {'Needs':[values]})
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This need already exists, if you intend to Edit this need, please change its name to something less ambiguous!"}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage("Need edited successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class NeedEditHandler(FormHandler):
    form = NeedEditForm

    def pre_fill_values(self, request, result):
        need = self.context.need
        values = need.unwrap()
        values['total'] = need.total
        values['ratio'] = need.equity_ratio
        result['values'][self.form.id] = values
        return super(NeedEditHandler, self).pre_fill_values(request, result)
