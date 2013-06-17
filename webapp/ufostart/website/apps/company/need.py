from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, REQUIRED, TextareaField, TagSearchField, IntField, HtmlAttrs
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from ufostart.website.apps.forms.controls import FileUploadField
from ufostart.website.apps.auth.social import AuthedFormHandler
from ufostart.website.apps.models.procs import CreateNeedProc, EditNeedProc, ApplyForNeedProc


def index(context, request):
    return {}

class ApplicationForm(BaseForm):
    id="Application"
    label = ""
    fields=[StringField('message', 'Message', REQUIRED)]
    @classmethod
    def on_success(cls, request, values):
        ApplyForNeedProc(request, {'token':request.root.need.token, 'Application': {'User':{'token':request.root.user.token}, 'message':values['message']}})
        request.session.flash(GenericSuccessMessage("You have applied for this need successfully. One of the team members will contact you shortly."), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("website_round_need", **request.root.urlArgs)}

class ApplicationHandler(AuthedFormHandler):
    form = ApplicationForm



class NeedCreateForm(BaseForm):
    id="NeedCreate"
    label = ""
    fields = [
        FileUploadField("picture", 'Picture')
        , StringField('name', "Need Name", REQUIRED)
        , IntField('cash', "Cash value", REQUIRED)
        , IntField('equity', "Equity value", REQUIRED)
        , TextareaField("description", "Description", REQUIRED, input_classes='x-high')
        , TagSearchField("Tags", "Related Tags", '/web/tag/search', 'Tags', attrs = HtmlAttrs(required=True, data_required_min = 3))
    ]
    @classmethod
    def on_success(cls, request, values):
        try:
            round = CreateNeedProc(request, {'Needs':[values], 'token': request.root.company.Round.token})
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This need already exists, if you intend to create this need, please change its name to something less ambiguous!"}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage("Need created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("website_company", **request.matchdict)}

class NeedCreateHandler(FormHandler):
    form = NeedCreateForm



class NeedEditForm(BaseForm):
    id="NeedEdit"
    label = ""
    fields = [
        FileUploadField("picture", 'Picture', group_classes='file-upload-control')
        , StringField('name', "Need Name", REQUIRED)
        , IntField('cash', "Cash value", REQUIRED)
        , IntField('equity', "Equity value", REQUIRED)
        , TextareaField("description", "Description", REQUIRED, input_classes='x-high')
        , TagSearchField("Tags", "Related Tags", '/web/tag/search', 'Tags', attrs = HtmlAttrs(required=True, data_required_min = 3))
    ]

    @classmethod
    def on_success(cls, request, values):
        values['token'] = request.matchdict['need']

        try:
            round = EditNeedProc(request, {'Needs':[values]})
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This need already exists, if you intend to Edit this need, please change its name to something less ambiguous!"}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage("Need edited successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("website_round_need", **request.matchdict)}

class NeedEditHandler(FormHandler):
    form = NeedEditForm

    def pre_fill_values(self, request, result):
        need = self.context.need
        values = need.unwrap()
        values['value'] = need.money_value
        values['ratio'] = need.equity_mix
        result['values'][self.form.id] = values
        return super(NeedEditHandler, self).pre_fill_values(request, result)
