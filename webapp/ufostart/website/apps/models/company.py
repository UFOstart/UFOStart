from hnc.apiclient import TextField, Mapping, ListField, DictField, DateTimeField
from hnc.apiclient.backend import ClientTokenProc

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
        return TEMPLATE_STYLE_KEYS[self.key]


GetAllCompanyTemplatesProc = ClientTokenProc("/web/template/list", result_cls=TemplateModel, root_key="Templates", result_list=True)
GetTemplateDetailsProc = ClientTokenProc("/web/template", result_cls=TemplateModel, root_key="Template")
GetAllNeedsProc = ClientTokenProc("/web/need/list", result_cls=NeedModel, root_key="Needs", result_list=True)


class RoundModel(Mapping):
    start = DateTimeField()
    token = TextField()
    Needs = ListField(DictField(NeedModel))


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
