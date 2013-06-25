from hnc.apiclient.backend import DBNotification
from hnc.forms.formfields import BaseForm, REQUIRED, StringField, TextareaField, HORIZONTAL_GRID
from pyramid.decorator import reify
from ufostart.website.apps.auth.social import AuthedFormHandler
from ufostart.website.apps.company.imp import SESSION_SAVE_TOKEN
from ufostart.website.apps.models.procs import GetAllCompanyTemplatesProc, GetTemplateDetailsProc, CreateCompanyProc
from ufostart.website.apps.forms.controls import FileUploadField


def basics(context, request):
    templates = GetAllCompanyTemplatesProc(request)
    return {'templates': templates}


def details(context, request):
    templateKey = request.matchdict['template']
    template = GetTemplateDetailsProc(request, {'key': templateKey})
    return {'template': template}


class CompanyCreateForm(BaseForm):
    id="CompanyCreate"
    label = ""
    fields=[
        StringField('name', 'Project Name', REQUIRED)
        , TextareaField("description", "Description", REQUIRED, input_classes='x-high')
        , FileUploadField('logo', 'Project Logo')
    ]
    @classmethod
    def on_success(cls, request, values):
        templateKey = request.matchdict['template']
        values['Template'] = {'key': templateKey}

        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            values['angelListId'] = al_company.id
            values['angelListToken'] = al_company.token

        try:
            company = CreateCompanyProc(request, {'token':request.root.user.token, 'Company':values})
        except DBNotification, e:
            if e.message == 'Company_Already_Exists':
                return {'success':False, 'errors': {'name': "Already exists"}}
            else:
                return {'success':False, 'message': 'Something went wrong: {}'.format(e.message)}
        else:
            return {'success':True, 'redirect': request.fwd_url("website_company", slug = request.root.user.getDefaultCompanySlug())}

class CreateProjectHandler(AuthedFormHandler):
    template = "ufostart:website/templates/company/setup/login.html"
    form = CompanyCreateForm

    def pre_fill_values(self, request, result):
        al_company = request.session.get(SESSION_SAVE_TOKEN)
        if al_company:
            result['values'][self.form.id] = {'name': al_company.name, 'description': al_company.high_concept, 'logo': al_company.thumb_url}
        return super(CreateProjectHandler, self).pre_fill_values(request, result)
