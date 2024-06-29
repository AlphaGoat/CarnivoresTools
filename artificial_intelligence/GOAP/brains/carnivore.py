from artificial_intelligence.GOAP import (World,
                                          Planner,
                                          ActionList)


if __name__ == "__main__":
    _brain = World()

    _carnivore_brain = Planner('is_hungry',
                               'is_near_kill',
                               'is_tired',
                               'is_secure',
                               'has_sighted_prey',
                               'has_smelled_prey',
                               'in_prey_los',
                               'has_sighted_player',
                               'has_smelled_player',
                               'in_player_los',
                               'in_concealment',
                               'is_near_player')

    _carnivore_brain.set_start_state(is_hungry=True,
                                     is_near_kill=False,
                                     is_tired=False,
                                     is_secure=True,
                                     has_sighted_prey=False,
                                     has_smelled_prey=False,
                                     in_prey_los=False,
                                     has_sighted_player=False,
                                     has_smelled_player=False,
                                     in_player_los=False,
                                     in_concealment=False,
                                     is_near_player=False)

    _carnivore_brain.set_goal_state(is_hungry=False)

    _carnivore_actions = ActionList()
    
    _carnivore_actions.add_condition('track_player',
                                     has_sighted_player=False,
                                     has_smelled_player=True,
                                     is_hungry=True)
    _carnivore_actions.add_reaction('track_player',
                                    has_sighted_player=True)

    _carnivore_actions.add_condition('flee_player',
                                     has_smelled_player=True,
                                     is_hungry=False)
    _carnivore_actions.add_reaction('flee_player',
                                    has_smelled_player=False)
