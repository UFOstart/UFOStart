from hnc.forms.formfields import BaseForm, REQUIRED, IntField, HtmlAttrs
from hnc.forms.handlers import FormHandler
from ufostart.website.apps.forms.controls import SanitizedHtmlField, FileUploadField
from ufostart.website.apps.models.procs import CreateFundingProc, InvestInCompanyProc


def index(context, request):
    return {}

class InvestmentForm(BaseForm):
    id="Investment"
    label = ""
    fields=[IntField("amount", "Amount", REQUIRED)]
    @classmethod
    def on_success(cls, request, values):
        values['User'] = {'token': request.root.user.token}
        data = {"token": request.context.round.token, "Funding": {"Investment": values}}
        InvestInCompanyProc(request, data)
        return {'success':True, 'redirect': request.resource_url(request.context)}

class InvestmentHandler(FormHandler):
    form = InvestmentForm


class FundingCreateForm(BaseForm):
    id="Funding"
    label = ""
    fields=[
     SanitizedHtmlField("description", "Deal Description", REQUIRED, input_classes='x-high')
     , IntField('amount', "Funding Amount", REQUIRED, input_classes='data-input amount lessThanEqual', maxlength = 10, max = 99999999)
     , IntField('valuation', "Company Valuation", REQUIRED, input_classes='data-input valuation', maxlength = 10, max = 99999999)
     , FileUploadField("contract", "Contract")
    ]
    @classmethod
    def on_success(cls, request, values):
        if values['amount'] > values['valuation']:
            return {'success':False, 'errors': {'amount': 'Amount needs to be lower than valuation!'}}
        data = {'token': request.context.round.token, 'Funding': values}
        CreateFundingProc(request, data)
        return {'success':True, 'redirect': request.resource_url(request.context)}

class FundingCreateHandler(FormHandler):
    form = FundingCreateForm


class FundingEditForm(FundingCreateForm):
    id="Funding"
    @classmethod
    def on_success(cls, request, values):
        if values['amount'] > values['valuation']:
            return {'success':False, 'errors': {'amount': 'Amount needs to be lower than valuation!'}}

        return {'success':True, 'redirect': request.resource_url(request.context)}

class FundingEditHandler(FormHandler):
    form = FundingEditForm