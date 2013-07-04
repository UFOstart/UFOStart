from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, StringField, REQUIRED, TextareaField, IntField, HtmlAttrs, HORIZONTAL_GRID, DecimalField, EmailField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from pyramid.httpexceptions import HTTPFound
from ufostart.website.apps.forms.controls import PictureUploadField, TagSearchField, CurrencyIntField
from ufostart.website.apps.models.company import NeedModel
from ufostart.website.apps.models.procs import CreateNeedProc, EditNeedProc, ApplyForNeedProc, ApproveApplicationProc, InviteToNeedProc, AddNeedToRound


class NeedIndexForm(BaseForm):
    id="NeedIndex"
    label = ""
    fields=[
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "email address", REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        user = request.root.user
        company = request.context.company

        values['invitorToken'] = user.token
        values['invitorName'] = user.name
        values['companySlug'] = company.slug
        values['companyName'] = company.name
        need = request.context.need
        values['Need'] = { "slug": need.slug, "name": need.name }

        InviteToNeedProc(request, {'Invite': values})

        request.session.flash(GenericSuccessMessage(u"You successfully invited {name} to this task!".format(**values)), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class NeedIndexHandler(FormHandler):
    form = NeedIndexForm




def accept_application(context, request):
    ApproveApplicationProc(request, {'token': context.application.token})
    request.session.flash(GenericSuccessMessage("The application has been accepted!"), "generic_messages")
    raise HTTPFound(request.resource_url(context.__parent__))



class ApplicationForm(BaseForm):
    id="Application"
    label = ""
    grid = HORIZONTAL_GRID
    fields=[StringField('message', 'Message', REQUIRED)]
    @classmethod
    def on_success(cls, request, values):
        ApplyForNeedProc(request, {'token':request.context.need.token, 'Application': {'User':{'token':request.root.user.token}, 'message':values['message']}})
        request.session.flash(GenericSuccessMessage("You have applied for this task successfully. One of the team members will contact you shortly."), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class ApplicationHandler(FormHandler):
    form = ApplicationForm



class NeedCreateForm(BaseForm):
    id="NeedCreate"
    label = ""
    fields = [
        PictureUploadField("picture", 'Picture', group_classes='file-upload-control')
        , StringField('name', "Title", REQUIRED)
        , CurrencyIntField('cash', "Cash Value", REQUIRED, input_classes='data-input cash', maxlength=9, currency='$')
        , CurrencyIntField('equity', "Equity Value", REQUIRED, input_classes='data-input equity', maxlength=9, currency='$')
        , TextareaField("customText", "Description", REQUIRED, input_classes='x-high')
        , TagSearchField("Tags", "Related Tags", '/web/tag/search', 'Tags', attrs = HtmlAttrs(required=True, data_required_min = 3, placeholder = "Add Tags"))
    ]
    @classmethod
    def on_success(cls, request, values):
        try:
            need = CreateNeedProc(request, {'Needs':[values], 'token': request.context.round.token})
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This task already exists, if you intend to create this task, please change its name to something less ambiguous!"}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage("Task created successfully!"), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class NeedCreateHandler(FormHandler):
    form = NeedCreateForm

    def pre_fill_values(self, request, result):
        result['need'] = NeedModel()
        return super(NeedCreateHandler, self).pre_fill_values(request, result)


class NeedEditForm(BaseForm):
    id="NeedEdit"
    label = ""
    fields = NeedCreateForm.fields

    @classmethod
    def on_success(cls, request, values):
        need = request.context.need
        round = request.context.round
        values['token'] = need.token
        newNeed = not need.added
        if newNeed:
            AddNeedToRound(request, {'Round': {'token':round.token, 'Needs':[{'token':need.token}]}})
        try:
            round = EditNeedProc(request, {'Needs':[values]})
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': "This task already exists, if you intend to Edit this task, please change its name to something less ambiguous!"}}
            else:
                raise e

        if newNeed:
            request.session.flash(GenericSuccessMessage("Task added to round!"), "generic_messages")
            return {'success':True, 'redirect': request.resource_url(request.context.__parent__)}
        else:
            request.session.flash(GenericSuccessMessage("Changes saved!"), "generic_messages")
            return {'success':True, 'redirect': request.resource_url(request.context)}

class NeedEditHandler(FormHandler):
    form = NeedEditForm

    def pre_fill_values(self, request, result):
        need = self.context.need
        round = self.context.round
        values = need.unwrap()
        values['total'] = need.total
        values['ratio'] = need.equity_ratio
        result['values'][self.form.id] = values
        return super(NeedEditHandler, self).pre_fill_values(request, result)

