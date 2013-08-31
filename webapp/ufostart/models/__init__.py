from hnc.apiclient import Mapping, TextField

__author__ = 'Martin'


class SlugTypeModel(Mapping):
    type = TextField()



class KeyValueModel(Mapping):
    key = TextField()
    Value = TextField()