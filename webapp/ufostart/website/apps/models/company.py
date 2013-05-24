from hnc.apiclient import TextField, Mapping, ListField, DictField
from hnc.apiclient.backend import ClientTokenProc

TEMPLATE_STYLE_KEYS = {
    'EARLY_STAGE_ECOMMERCE':'ecommerce'
    , 'HI-TECH':'hitech'
    , 'INTERNATIONALISING':'internat'
    , 'JUST_GETTING_STARTED':'started'
    , 'SEED_STAGE':'seed'
    , 'SERIES_B':'seriesb'
}



class NeedModel(Mapping):
    key = TextField()
    name = TextField()


class TemplateModel(Mapping):
    key = TextField()
    name = TextField()
    Need = ListField(DictField(NeedModel))

    def getStyleKey(self):
        return TEMPLATE_STYLE_KEYS[self.key]


GetAllCompanyTemplatesProc = ClientTokenProc("/web/template/list", result_cls=TemplateModel, root_key="Templates", result_list=True)
GetTemplateDetailsProc = ClientTokenProc("/web/template", result_cls=TemplateModel, root_key="Template")
GetAllNeedsProc = ClientTokenProc("/web/need/list", result_cls=NeedModel, root_key="Needs", result_list=True)



class CompanyModel(Mapping):
    token = TextField()
    Template = DictField(TemplateModel)

SetCompanyTemplateProc = ClientTokenProc("/web/company/template")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)



