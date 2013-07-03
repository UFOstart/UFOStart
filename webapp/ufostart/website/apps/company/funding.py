from hnc.forms.formfields import BaseForm, REQUIRED, IntField
from hnc.forms.handlers import FormHandler
from ufostart.website.apps.forms.controls import SanitizedHtmlField
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
    id="FundingCreate"
    label = ""
    fields=[
     SanitizedHtmlField("description", "Deal Description", REQUIRED, input_classes='x-high')
     , IntField('amount', "Amount", min = 1)
     , IntField('valuation', "Valuation", min = 1)
    ]
    @classmethod
    def on_success(cls, request, values):
        data = {'token': request.context.round.token, 'Funding': values}
        CreateFundingProc(request, data)
        return {'success':True, 'redirect': request.resource_url(request.context, "funding")}

class FundingCreateHandler(FormHandler):
    form = FundingCreateForm


class FundingEditForm(FundingCreateForm):
    id="FundingEdit"
    @classmethod
    def on_success(cls, request, values):
        return {'success':True, 'redirect': request.fwd_url("")}

class FundingEditHandler(FormHandler):
    form = FundingEditForm