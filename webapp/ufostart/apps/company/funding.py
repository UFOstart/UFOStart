# coding=utf-8
from hnc.forms.formfields import REQUIRED, IntField, HtmlAttrs
from hnc.forms.handlers import FormHandler
from ufostart.lib.baseviews import BaseForm
from ufostart.apps.forms.controls import SanitizedHtmlField, FileUploadField, CurrencyIntField
from ufostart.models.procs import CreateFundingProc, InvestInCompanyProc


def index(context, request):
    return {}

class InvestmentForm(BaseForm):
    id="Investment"
    label = ""
    fields=[
        CurrencyIntField('amount', "Investment Amount", REQUIRED, input_classes='data-input amount', maxlength=7)
    ]
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
     , CurrencyIntField('amount', "Funding Amount", REQUIRED, input_classes='data-input amount', maxlength=7)
     , CurrencyIntField('valuation', "Company Valuation", REQUIRED, input_classes='data-input valuation', maxlength=7)
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

class FundingEditHandler(FormHandler):
    form = FundingCreateForm

    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = request.context.round.Funding.unwrap()
        return super(FundingEditHandler, self).pre_fill_values(request, result)
