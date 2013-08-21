from hnc.apiclient import Mapping, TextField

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
    def getLabel(self, request):return self.label



class TaskCategoriesModel(NamedModel):
    name = TextField()




TASK_CATEGORIES = [
    TaskCategoriesModel(name = 'OPERATIONS')
    , TaskCategoriesModel(name = 'MARKETING')
    , TaskCategoriesModel(name = 'SALES')
    , TaskCategoriesModel(name = 'TECH')
]