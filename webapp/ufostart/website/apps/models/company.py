from hnc.apiclient import TextField, Mapping, ListField, DictField
from hnc.apiclient.backend import ClientTokenProc



class NeedModel(Mapping):
    name = TextField()


class TemplateModel(Mapping):
    name = TextField()
    Need = ListField(DictField(NeedModel))

class TemplateListModel(Mapping):
    name = TextField()

GetAllCompanyTemplatesProc = ClientTokenProc("/web/template/list", result_cls=TemplateListModel, root_key="Templates")
GetTemplateDetailsProc = ClientTokenProc("/web/template", result_cls=TemplateModel, root_key="Template")
GetAllNeedsProc = ClientTokenProc("/web/need/list", result_cls=NeedModel, root_key="Needs", result_list=True)



class CompanyModel(Mapping):
    token = TextField()
    Template = DictField(TemplateModel)

SetCompanyTemplateProc = ClientTokenProc("/web/company/template")
GetCompanyProc = ClientTokenProc("/web/company", root_key="Company", result_cls=CompanyModel)



