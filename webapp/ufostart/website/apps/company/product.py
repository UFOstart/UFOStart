from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, MultipleFormField, REQUIRED, StringField, RadioChoice, NullConfigModel, TextareaField, HORIZONTAL_GRID
from hnc.forms.handlers import FormHandler
from ufostart.website.apps.auth.social import require_login
from ufostart.website.apps.company.imp import SESSION_SAVE_TOKEN
from ufostart.website.apps.models.procs import AddProductOfferProc, PledgeCompanyProc, CreateProductProc
from ufostart.website.apps.forms.controls import FileUploadField




class ProductCreateForm(BaseForm):
    id="ProductCreate"
    label = ""
    grid = HORIZONTAL_GRID
    fields=[
        StringField('name', "Name")
        , TextareaField('description', "Description", input_classes="x-high")
        , FileUploadField("picture", "Product Picture")
        , StringField("video", "Vimeo/YouTube")
    ]
    @classmethod
    def on_success(cls, request, values):
        data = {'token': request.context.company.Round.token, 'Product': values}
        result = CreateProductProc(request, data)
        return {'success':True, 'redirect': request.fwd_url("website_company_product", **request.root.urlArgs)}

class ProductCreateHandler(FormHandler):
    form = ProductCreateForm

    def pre_fill_values(self, request, result):
        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            result['values'][self.form.id] = {
                'name': al_company.name
                , 'description': al_company.product_desc
                , 'picture': al_company.getFirstScreenShot()
                , 'video' : al_company.video_url
            }
        return super(ProductCreateHandler, self).pre_fill_values(request, result)





class ProductEditForm(ProductCreateForm):
    id="ProductEdit"
    @classmethod
    def on_success(cls, request, values):
        product = request.root.company.Round.Product
        values['token'] = product.token
        data = {'token': request.context.company.Round.token, 'Product': values}
        result = CreateProductProc(request, data)
        return {'success':True, 'redirect': request.fwd_url("website_company_product", **request.root.urlArgs)}


class ProductEditHandler(FormHandler):
    form = ProductEditForm
    def pre_fill_values(self, request, result):
        product = request.root.company.Round.Product
        result['values'][self.form.id] = product.unwrap()
        return super(ProductEditHandler, self).pre_fill_values(request, result)








class OfferChoiceField(RadioChoice):
    pass


def offer_choices(request):
    return request.root.company.Round.Product.Offers



class OffersField(MultipleFormField):
    template = 'ufostart:website/templates/company/controls/offer.html'
    add_more_link_label = 'Add Offer'
    fields = [
        StringField('name', "Offer", REQUIRED)
    ]


class ProductOfferForm(BaseForm):
    id="ProductOffer"
    label = ""
    grid = HORIZONTAL_GRID
    fields=[
        OffersField("Offers")
    ]
    @classmethod
    def on_success(cls, request, values):
        round = request.root.company.Round
        values['token'] = round.Product.token
        AddProductOfferProc(request, {'Product': values})
        return {'success':True, 'redirect': request.rld_url()}


class ProductPledgeForm(BaseForm):
    id="ProductPledge"
    grid = HORIZONTAL_GRID
    label = ""
    fields=[
        OfferChoiceField('offer', 'Your Offer', offer_choices, REQUIRED, input_classes='radio')
        , TextareaField('comment', 'Comment', REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        round = request.root.company.Round
        user = request.root.user

        values.update({'name': user.name, 'network':'ufo', 'networkId': user.token, 'picture':user.getPicture()})
        data = {'token': round.token, 'Pledge' : values}
        try:
            PledgeCompanyProc(request, data)
        except DBNotification, e:
            if e.message == 'AlreadyPledged':
                pass
            else:
                raise e

        return {'success':True, 'redirect': request.rld_url()}

class ProductOfferHandler(FormHandler):
    forms = [ProductOfferForm, ProductPledgeForm]
    def __init__(self, context=None, request=None):
        if not context.company.product_is_setup:
            if context.isTeamMember:
                request.fwd("website_company_product_create", **context.urlArgs)
            else:
                request.fwd("website_company", **context.urlArgs)
        super(ProductOfferHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        company = request.root.company
        result['company'] = company
        result['product'] = company.Round.Product
        if company.Round and company.Round.Product:
            result['values']['ProductOffer'] = company.Round.Product.unwrap()
        return result



@require_login('ufostart:website/templates/auth/login.html')
def login(context, request):
    request.fwd("website_company_product", **context.urlArgs)


