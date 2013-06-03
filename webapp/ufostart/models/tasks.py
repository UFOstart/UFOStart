from hnc.apiclient import Mapping, TextField


class TaskCategoriesModel(Mapping):
    name = TextField()




TASK_CATEGORIES = [
    TaskCategoriesModel(name = 'Operation')
    , TaskCategoriesModel(name = 'Marketing')
    , TaskCategoriesModel(name = 'Sales')
    , TaskCategoriesModel(name = 'Technology')
]