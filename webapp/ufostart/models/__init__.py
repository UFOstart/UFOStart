from hnc.apiclient import Mapping, TextField, ListField, DictField

__author__ = 'Martin'


class SlugTypeModel(Mapping):
    type = TextField()



class KeyValueModel(Mapping):
    key = TextField()
    value = TextField()


class ContentModel(Mapping):
    Static = ListField(DictField(KeyValueModel))