from hnc.apiclient import Mapping, TextField


class TaskCategoriesModel(Mapping):
    name = TextField()




TASK_CATEGORIES = [
    TaskCategoriesModel(name = 'OPERATIONS')
    , TaskCategoriesModel(name = 'MARKETING')
    , TaskCategoriesModel(name = 'SALES')
    , TaskCategoriesModel(name = 'TECH')
]