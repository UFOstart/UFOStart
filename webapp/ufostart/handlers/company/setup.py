from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import  REQUIRED, StringField, ChoiceField, URLField
from hnc.forms.handlers import FormHandler
from pyramid.i18n import TranslationStringFactory
from ufostart.lib.baseviews import BaseForm
from ufostart.handlers.auth.imp import SESSION_SAVE_TOKEN
from ufostart.models.procs import CreateCompanyProc, EditCompanyProc
from ufostart.handlers.forms.controls import PictureUploadField, PictureGalleryUploadField, CleanHtmlField, SanitizedHtmlField, SlideshareField, VideoUrlField, UniqueNameField
from ufostart.models.tasks import NamedModel


_ = TranslationStringFactory("uforeloaded")

def basics(context, request):
    return {'templates': context.templates}

def details(context, request):
    return {'template': context.template}


class CompanyCreateForm(BaseForm):
    id="CompanyCreate"
    label = ""
    fields=[
        PictureUploadField('logo', _('CompanyCreate.Form.Label:Logo'), REQUIRED, picWidth=250, picHeight=170)
        , StringField('name', _('CompanyCreate.Form.Label:Name'), REQUIRED)
        , UniqueNameField("slug", _('CompanyCreate.Form.Label:UFOstart Url'), thing_name = 'company name')
        , URLField("companyUrl", _('CompanyCreate.Form.Label:Project Website'))
        , CleanHtmlField('pitch', _('CompanyCreate.Form.Label:Slogan'), REQUIRED, max = 90)
        , SanitizedHtmlField("description", _('CompanyCreate.Form.Label:Description'), REQUIRED, input_classes='x-high')
        , PictureGalleryUploadField('Pictures', _('CompanyCreate.Form.Label:Drag multiple images into your gallery'))
        , StringField("video", _('CompanyCreate.Form.Label:Paste a Vimeo or Youtube Url'))
        , StringField("slideShare", _('CompanyCreate.Form.Label:Paste a Slideshare Url'))
        , ChoiceField("currency", _('CompanyCreate.Form.Label:Project Currency'), optionGetter=lambda s: [NamedModel(name = 'EUR'), NamedModel(name = 'USD')])
        , URLField("socialMediaUrl", _('CompanyCreate.Form.Label:Project Blog Url'))
    ]

    @classmethod
    def on_success(cls, request, values):
        templateKey = request.context.__name__
        if isinstance(values.get('pictures'), basestring):values['Pictures'] = [values['Pictures']]
        values['Pictures'] = [{'url':url} for url in values['Pictures']]
        values['Template'] = {'key': templateKey}

        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            values['angelListId'] = al_company.id
            values['angelListToken'] = al_company.token
            del request.session[SESSION_SAVE_TOKEN]

        try:
            company = CreateCompanyProc(request, {'token':request.root.user.token, 'Company':values})
        except DBNotification, e:
            if e.message == 'Company_Already_Exists':
                return {'success':False, 'errors': {'name': _('CompanyCreate.Form.Error:Already exists')}}
            else:
                return {'success':False, 'message': 'Something went wrong: {}'.format(e.message)}
        else:
            return {'success':True, 'redirect': request.root.round_url(request.root.user.getDefaultCompanySlug(), '1')}


class CreateProjectHandler(FormHandler):
    form = CompanyCreateForm

    def pre_fill_values(self, request, result):
        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            result['values'][self.form.id] = {
                        'name': al_company.name
                        , 'pitch': al_company.high_concept
                        , 'description': al_company.product_desc
                        , 'logo': al_company.logo_url
                        , 'video': al_company.video_url
                        , 'Pictures': [{'url':unicode(scr)} for scr in al_company.screenshots]
                    }
        return super(CreateProjectHandler, self).pre_fill_values(request, result)



class CompanyEditForm(BaseForm):
    id="CompanyEdit"
    label = ""
    fields=[
        PictureUploadField('logo', _('CompanyCreate.Form.Label:Logo'), REQUIRED, picWidth=250, picHeight=170)
        , StringField('name', _('CompanyCreate.Form.Label:Name'), REQUIRED)
        , URLField("companyUrl", _('CompanyCreate.Form.Label:Project Website'))
        , CleanHtmlField('pitch', _('CompanyCreate.Form.Label:Slogan'), REQUIRED, max = 90)
        , SanitizedHtmlField("description", _('CompanyCreate.Form.Label:Description'), REQUIRED, input_classes='x-high')
        , PictureGalleryUploadField('Pictures', _('CompanyCreate.Form.Label:Drag multiple images into your gallery'))

        , StringField("video", _('CompanyCreate.Form.Label:Paste a Vimeo or Youtube Url'))
        , StringField("slideShare", _('CompanyCreate.Form.Label:Paste a Slideshare Url'))
        , URLField("socialMediaUrl", _('CompanyCreate.Form.Label:Project Blog Url'))
    ]

    @classmethod
    def on_success(cls, request, values):
        company = request.context.company

        if isinstance(values.get('Pictures'), basestring):values['Pictures'] = [values['Pictures']]
        values['Pictures'] = [{'url':url} for url in values['Pictures']]
        values['token'] = company.token

        try:
            company = EditCompanyProc(request, values)
        except DBNotification, e:
            if e.message == 'Company_Already_Exists':
                return {'success':False, 'errors': {'name': _('CompanyCreate.Form.Error:Already exists')}}
            else:
                return {'success':False, 'message': 'Something went wrong: {}'.format(e.message)}
        else:
            return {'success':True, 'redirect': request.resource_url(request.context)}


class EditProjectHandler(FormHandler):
    form = CompanyEditForm

    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = request.context.company.unwrap(sparse = True)
        return super(EditProjectHandler, self).pre_fill_values(request, result)
