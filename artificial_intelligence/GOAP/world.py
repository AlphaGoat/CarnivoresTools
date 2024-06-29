


class World():
    def __init__(self):
        self.planners = []
        self.plans = []

    def add_planner(self, planner):
        self.planners.append(planner)

    def calculate(self):
        self.plans = []

        for planner in self.planners:
            self.plans.append(planner.calculate())

    def get_plan(self, debug=False):
        _plans = {}

        for plan in self.plans:
            _plan_cost = sum([action['g'] for action in plan])

            if _plan_cost in _plans:
                _plans[_plan_cost].append(plan)
            else:
                _plans[_plan_cost] = [plan]

        _sorted_plans = sorted(_plans.keys())

        if debug:
            _i = 1
            for plan_score in _sorted_plans:
                for plan in _plans[plan_score]:
                    print(_i)

                _i += 1
                print("\nTotal cost: %s\n" % plan_score)

        return [_plans[p][0] for p in _sorted_plans]
