# coding=utf-8
from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import StringField, REQUIRED, TextareaField, IntField, HtmlAttrs, HORIZONTAL_GRID, DecimalField, EmailField, CheckboxField, CheckboxPostField, TypeAheadField
from hnc.forms.handlers import FormHandler
from hnc.forms.messages import GenericSuccessMessage
from pyramid.httpexceptions import HTTPFound
from ufostart.lib.baseviews import BaseForm
from ufostart.handlers.forms.controls import PictureUploadField, TagSearchField, CurrencyIntField, SanitizedHtmlField, ServiceSearchField
from ufostart.models.company import NeedModel
from ufostart.models.procs import CreateNeedProc, EditNeedProc, ApplyForNeedProc, ApproveApplicationProc, InviteToNeedProc, AddNeedToRound

_ = lambda s:s

class NeedIndexForm(BaseForm):
    id="Needinvite"
    label = ""
    fields=[
        StringField("name", _("TaskDetailsPage.Invite.FormLabel.Name"), REQUIRED)
        , EmailField("email", _("TaskDetailsPage.Invite.FormLabel.EmailAddress"), REQUIRED)
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
    fields=[StringField('message', _("TaskDetailsPage.Apply.FormLabel.Message"), REQUIRED)]
    @classmethod
    def on_success(cls, request, values):
        _ = request._
        ApplyForNeedProc(request, {'token':request.context.need.token, 'Application': {'User':{'token':request.root.user.token}, 'message':values['message']}})
        request.session.flash(GenericSuccessMessage(_("TaskDetailsPage.Apply.SuccessMessage.You have applied for this task successfully. One of the team members will contact you shortly.")), "generic_messages")
        return {'success':True, 'redirect': request.resource_url(request.context)}

class ApplicationHandler(FormHandler):
    forms = [ApplicationForm, NeedIndexForm]



class NeedCreateForm(BaseForm):
    id="NeedCreate"
    label = ""
    fields = [
        PictureUploadField("picture", _("TaskSetup.FormLabel.Picture"), group_classes='file-upload-control')
        , TypeAheadField('name', _("TaskSetup.FormLabel.Title"), '/web/need/name', 'Needs', attrs = REQUIRED, js_module = "views/company/need_switch", api_allow_new = True)
        , CheckboxPostField('parttime', _("TaskSetup.FormLabel.is part time"))
        , CurrencyIntField('cash', _("TaskSetup.FormLabel.Cash Value"), HtmlAttrs(required=True, data_control_help=_("TaskSetup.FormLabel.Cash Value.Help")), input_classes='data-input cash', maxlength=8)
        , CurrencyIntField('equity', _("TaskSetup.FormLabel.Equity Value"), HtmlAttrs(required=True, data_control_help=_("TaskSetup.FormLabel.Equity Value")), input_classes='data-input equity', maxlength=8)
        , SanitizedHtmlField("customText", _("TaskSetup.FormLabel.Description"), REQUIRED, input_classes='x-high')
        , TagSearchField("Tags", _("TaskSetup.FormLabel.Related Tags"), '/web/tag/search', 'Tags', attrs = HtmlAttrs(required=True, data_required_min = 3, placeholder = "Add Tags"))
        , ServiceSearchField("Services", _("TaskSetup.FormLabel.Related Services"), '/web/service/search', 'Services', attrs = HtmlAttrs(placeholder = "Add Services"))
    ]
    @classmethod
    def on_success(cls, request, values):
        _ = request._
        try:
            need = CreateNeedProc(request, {'Needs':[values], 'token': request.context.round.token})
        except DBNotification, e:
            if e.message == 'Need_Already_Exists':
                return {'success':False, 'errors': {'name': _("TaskSetup.ErrorMessage.This task already exists, if you intend to create this task, please change its name to something less ambiguous!")}}
            else:
                raise e

        request.session.flash(GenericSuccessMessage(_("TaskSetup.SuccessMessage.Task created successfully!")), "generic_messages")
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
        _ = request._
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
                return {'success':False, 'errors': {'name': _("TaskSetup.ErrorMessage.This task already exists, if you intend to Edit this task, please change its name to something less ambiguous!")}}
            else:
                raise e

        if newNeed:
            request.session.flash(GenericSuccessMessage(_("TaskSetup.SuccessMessage.Task added to round!")), "generic_messages")
            return {'success':True, 'redirect': request.resource_url(request.context.__parent__)}
        else:
            request.session.flash(GenericSuccessMessage(_("TaskSetup.SuccessMessage.Changes saved!")), "generic_messages")
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

