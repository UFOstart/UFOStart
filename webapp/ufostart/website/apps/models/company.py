from hnc.apiclient import TextField, Mapping, ListField, DictField
from hnc.apiclient.backend import ClientTokenProc



class NeedModel(Mapping):
    key = TextField()
    name = TextField()


class TemplateModel(Mapping):
    key = TextField()
    name = TextField()
    Need = ListField(DictField(NeedModel))

    def getStyleKey(self):
        return self.key.lower()


GetAllCompanyTemplatesProc = ClientTokenProc("/web/template/list", result_cls=TemplateModel, root_key="Templates", result_list=True)
GetTemplateDetailsProc = ClientTokenProc("/web/template", result_cls=TemplateModel, root_key="Template")
GetAllNeedsProc = ClientTokenProc("/web/need/list", result_cls=NeedModel, root_key="Needs", result_list=True)



class CompanyModel(Mapping):
    token = TextField()
    Template = DictField(TemplateModel)

SetCompanyTemplateProc = ClientTokenProc("/web/company/template")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)



