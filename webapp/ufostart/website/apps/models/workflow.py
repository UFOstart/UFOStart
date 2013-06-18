from collections import OrderedDict
from operator import attrgetter
from hnc.apiclient import Mapping, TextField, IntegerField, BooleanField, DictField, ListField
from pyramid.decorator import reify


def stage_sorter(a,b):
    if a.order == b.order:
        return 0
    elif a.order is None:
        return 1
    elif b.order is None:
        return -1
    else:
        return cmp(a.order,b.order)

class StageModel(Mapping):
    name = TextField()
    order = IntegerField()
    completed = BooleanField()
    skippable = BooleanField()

    def canBeSkipped(self):
        return self.skippable

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
