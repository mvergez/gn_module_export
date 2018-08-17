from enum import Enum


class Node:
    def __init__(self, id):
        self.ID = id


class Collection(Node):
    def __init__(self, id, label, rules):
        self.label = label
        self.ruleset = rules
        super.__init__(self, id)

    def items(self):
        pass


class CollectionRuleSet:
    def __init__(self, rules):
        self.rules = rules


class CollectionRule:
    def __init__(self, column, relation=None, condition=None):
        self.header = column
        self.op = relation
        self.val = condition


class CollectionRuleField(Enum):
    pass


CollectionRelation = Enum(
    'EQUALS', 'NOT_EQUALS',
    'CONTAINS', 'NOT_CONTAINS',
    'GREATER_THAN', 'LESS_THAN',
    'STARTS_WITH', 'ENDS_WITH',
    module=__name__)