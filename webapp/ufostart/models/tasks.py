from hnc.apiclient import Mapping, TextField
from translationstring import TranslationStringFactory

_ = TranslationStringFactory("ufo")

class NamedModel(Mapping):
    name = TextField()
    def getKey(self, request):return self.name
    def getLabel(self, request):return self.name

    def toQuery(self):
        return {'value':self.name, 'label': self.name}

class RoleModel(NamedModel):
    key = TextField()
    label = TextField()
    def getKey(self, request):return self.key
    def getLabel(self, request):return request._(self.label)


ROLES = [RoleModel(key = "FOUNDER", label = _("RoleLabel.Founder")), RoleModel(key = "TEAM_MEMBER", label = _("RoleLabel.Team Member")), RoleModel(key = "ADVISOR", label = _("RoleLabel.Advisor"))]


class TaskCategoriesModel(NamedModel):
    name = TextField()

TASK_CATEGORIES = [
    TaskCategoriesModel(name = 'OPERATIONS')
    , TaskCategoriesModel(name = 'MARKETING')
    , TaskCategoriesModel(name = 'SALES')
    , TaskCategoriesModel(name = 'TECH')
    , TaskCategoriesModel(name = 'MISC')
]
