


class ActionList():
    def __init__(self):
        self.conditions = {}
        self.reactions = {}
        self.weights = {}

    def add_condition(self, key, **kwargs):
        if not key in self.weights:
            self.weights[key] = 1

        if not key in self.conditions:
            self.conditions[key] = kwargs
            return

        self.conditions[key].update(kwargs)

    def add_reaction(self, key, **kwargs):
        if not key in self.conditions:
            raise Exception('Trying to add reaction \'%s\' without matching condition.' % key)

        if not key in self.reactions:
            self.reactions[key] = kwargs
            
            return

        self.reactions[key].update(kwargs)

    def set_weight(self, key, value):
        if not key in self.conditions:
            raise Exception('Trying to set weight \'%s\' without matching condition.' % key)

        self.weights[key] = value
