from collections import OrderedDict
from operator import attrgetter
from hnc.apiclient import Mapping, TextField, IntegerField, BooleanField, DictField, ListField
from pyramid.decorator import reify

def workflow_check(name):
    def f(self):
        try:
            return self.Workflow.stagesMap[name].done
        except (AttributeError, ValueError, KeyError):
            return False
    return f

def stage_sorter(a,b):
    if a.order == b.order:
        return 0
    elif a.order is None:
        return 1
    elif b.order is None:
        return -1
    else:
        return cmp(a.order,b.order)

STAGE_NAMES = {
    u'CREATE_COMPANY':'Setup Project'
    , u'CREATE_PRODUCT':'Customize Product'
    , u'CUSTOMISE_NEEDS': 'Customize Needs'
    , u'INVITE_TEAM':'Invite Team Members'
    , u'PUBLISH': 'Publish Round'
}


class StageModel(Mapping):
    name = TextField()
    order = IntegerField()
    completed = BooleanField()
    skippable = BooleanField()

    def canBeSkipped(self):
        return self.skippable

    @property
    def display_name(self):
        return STAGE_NAMES[self.name]
    @property
    def slug(self):
        return self.name.replace("_", "-").lower()

class WorkflowBluePrintModel(Mapping):
    name = TextField()
    enforceOrder = BooleanField()
    stages = ListField(DictField(StageModel), name = "Stage")

    @reify
    def sortedStages(self):
        return sorted(self.stages, cmp = stage_sorter)

    @reify
    def stagesMap(self):
        return OrderedDict([(stage.name, stage) for stage in self.sortedStages])

    @reify
    def reachableStages(self):
        result = []
        reachable = 0
        for stage in self.sortedStages:
            if stage.completed:
                result.append(stage)
                reachable = stage.order
            elif stage.order <= reachable + 1:
                result.append(stage)
        return result

    def isEnabled(self, stage):
        return stage in map(attrgetter('name'), self.reachableStages)

class WorkflowModel(WorkflowBluePrintModel):
    def isComplete(self):
        return len(filter(attrgetter("completed"), self.stages)) == len(self.stages)
    def hasStarted(self):
        return len(filter(attrgetter("completed"), self.stages)) > 0
    def getActiveStage(self):
        for stage in self.sortedStages:
            if not stage.completed: return stage
    def canPublish(self):
        a_s = self.getActiveStage()
        return a_s.name == 'PUBLISH' if a_s else False