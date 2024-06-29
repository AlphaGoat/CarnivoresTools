from utils import astar


class Planner():
    def __init__(self, *keys):
        self.start_state = None
        self.goal_state = None
        self.values = {k: -1 for k in keys}
        self.action_list = None

    def state(self, **kwargs):
        _new_state = self.values.copy()
        _new_state.update(kwargs)

        return _new_state

    def set_start_state(self, **kwargs):
        _invalid_states = set(kwargs.keys()) - set(self.values.keys())

        if _invalid_states:
            raise Exception('Invalid states for world start state: %s' %
                ','.join(list(_invalid_states)))
        
        self.start_state = self.state(**kwargs)

    def set_goal_state(self, **kwargs):
        _invalid_states = set(kwargs.keys()) - set(self.values.keys())

        if _invalid_states:
            raise Exception('Invalid states for world start state: %s' %
                ','.join(list(_invalid_states)))

        self.goal_state = self.state(**kwargs)

    def set_action_list(self, action_list):
        self.action_list = action_list

    def calculate(self):
        return astar(self.start_state,
                     self.goal_state,
                     {c: self.action_list.conditions[c].copy() for c in self.action_list.conditions},
                     {r: self.action_list.reactions[r].copy() for r in self.action_list.reactions},
                      self.action_list.weights.copy())

