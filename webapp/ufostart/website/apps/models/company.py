from datetime import datetime, timedelta
from babel.dates import format_date
from hnc.apiclient import TextField, Mapping, ListField, DictField, DateTimeField
from hnc.apiclient.backend import ClientTokenProc
from pyramid.decorator import reify

TEMPLATE_STYLE_KEYS = {
    'EARLY_STAGE_ECOMMERCE':'ecommerce'
    , 'HI-TECH':'hitech'
    , 'INTERNATIONALISING':'internat'
    , 'JUST_GETTING_STARTED':'started'
    , 'SEED_STAGE':'seed'
    , 'SERIES_B':'seriesb'
}

class ExpertModel(Mapping):
    linkedinId = TextField()
    firstName = TextField()
    lastName = TextField()
    picture = TextField()
    introLinkedinId = TextField()
    introFirstName = TextField()
    introLastName = TextField()
    introPicture = TextField()

    def getExpertPicture(self):
        return self.picture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"
    def getExpertName(self):
        return u"{} {}".format(self.firstName, self.lastName)

    def getIntroName(self):
        return u"{} {}".format(self.introFirstName, self.introLastName)
    def getIntroPicture(self):
        return self.introPicture or "//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"



class ServiceModel(Mapping):
    name = TextField()
    url = TextField()
    worker = TextField()
    picture = TextField()
    def getWorkerName(self):
        return self.worker
    def getWorkerPicture(self):
        return self.picture or"//www.gravatar.com/avatar/00000000000000000000000000000000?d=mm"

class NeedModel(Mapping):
    key = TextField()
    name = TextField()
    Service = DictField(ServiceModel)
    Expert = DictField(ExpertModel)


class TemplateModel(Mapping):
    key = TextField()
    name = TextField()
    Need = ListField(DictField(NeedModel))

    def getStyleKey(self):
        if not self.key:
            self.key = self.name.replace(" ", "_").upper()
        return TEMPLATE_STYLE_KEYS[self.key]


GetAllCompanyTemplatesProc = ClientTokenProc("/web/template/list", result_cls=TemplateModel, root_key="Templates", result_list=True)
GetTemplateDetailsProc = ClientTokenProc("/web/template", result_cls=TemplateModel, root_key="Template")
GetAllNeedsProc = ClientTokenProc("/web/need/list", result_cls=NeedModel, root_key="Needs", result_list=True)


class RoundModel(Mapping):
    start = DateTimeField()
    token = TextField()
    Needs = ListField(DictField(NeedModel))

    @reify
    def expiry(self):
        return self.start+timedelta(90)

    def getExpiryDays(self, singular = "{} Day Left", plural="{} Days Left", closed = "Closed"):
        delta = (self.start+timedelta(90)) - datetime.today()
        if 0 < delta.days <= 1:
            return singular.format(delta.days)
        elif delta.days > 1:
            return plural.format(delta.days)
        else:
            return closed
    def getExpiryDate(self):
        return format_date(self.start+timedelta(90), format="medium", locale='en')


class CompanyModel(Mapping):
    token = TextField()
    Template = DictField(TemplateModel)
    Round = DictField(RoundModel)
    Rounds = ListField(DictField(RoundModel))



GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)

SetCompanyTemplateProc = ClientTokenProc("/web/company/template")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)

CreateRoundProc = ClientTokenProc("/web/round/create", root_key="Round", result_cls=RoundModel)
GetRoundProc = ClientTokenProc("/web/round", root_key="Round", result_cls=RoundModel)
