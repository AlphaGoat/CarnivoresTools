

def distance_to_state(state1, state2):
    _scored_keys = set()
    _score = 0

    for key in state2.keys():
        _value = state2[key]

        if _value == -1:
            continue

        if not _value == state1[key]:
            _score += 1

        _scored_keys.add(key)

    for key in state1.keys():
        if key in _scored_keys:
            continue

        _value = state1[key]

        if _value == -1:
            continue

        if not _value == state1[key]:
            _score += 1

        return _score


def conditions_are_met(state1, state2):
    for key in state2.keys():
        _value = state2[key]

        if _value == -1:
            continue

        if not state1[key] == state2[key]:
            return False

    return True


def node_in_list(node, node_list):
    for next_node in node_list.values():
        if node['state'] == next_node['state'] and node['name'] == next_node['name']:
            return True

    return False


def create_node(path, state, name=''):
    path['node_id'] += 1
    path['nodes'][path['node_id']] = {'state': state, 'f': 0, 'g': 0, 'h': 0, 'p_id': None, 'id': path['node_id']}

    return path['nodes'][path['node_id']]


def astar(start_state, goal_state, actions, reactions, weight_table):
    _path = {'nodes': {},
             'node_id': 0,
             'goal': goal_state,
             'actions': actions,
             'reactions': reactions,
             'weight_table': weight_table,
             'action_nodes': {},
             'olist': {},
             'clist': {}}

    _start_node = create_node(_path, start_state, name='start')
    _start_node['g'] = 0
    _start_node['h'] = distance_to_state(start_state, goal_state)
    _start_node['f'] = _start_node['g'] + _start_node['h']
    _path['olist'][_start_node['id']] = _start_node

    for action in actions:
        _path['action_nodes'][action] = create_node(_path, actions[action], name=action)

    return walk_path(_path)


def walk_path(path):
    node = None
    
    _clist = path['clist']
    _olist = path['olist']

    while len(_olist):
        _lowest = {'node': None, 'f': 9000000}

        for next_node in _olist.values():
            if not _lowest['node'] or next_node['f'] < _lowest['f']:
                _lowest['node'] = next_node['id']
                _lowest['f'] = next_node['f']

        if _lowest['node']:
            node = path['nodes'][_lowest['node']]

        else:
            return

        # Remove node with lowest rank
        del _olist[node['id']]

        if conditions_are_met(node['state'], path['goal']):
            _path = []

            while node['p_id']:
                _path.append(node)

                node = path['nodes'][node['p_id']]

            _path.reverse()

            return _path

        _clist[node['id']] = node

        _neighbors = []

        for action_name in path['action_nodes']:
            if not conditions_are_met(node['state'], path['action_nodes'][action_name]['state']):
                continue

            path['node_id'] += 1

            _c_node = node.copy()
            _c_node['state'] = node['state'].copy()
            _c_node['id'] = path['node_id']
            _c_node['name'] = action_name

            for key in path['reactions'][action_name]:
                _value = path['reactions'][action_name][key]

                if _value == -1:
                    continue

                _c_node['state'][key] = _value

            path['nodes'][_c_node['id']] = _c_node
            _neighbors.append(_c_node)

        for next_node in _neighbors:
            _g_cost = node['g'] + path['weight_table'][next_node['name']]
            _in_olist, _in_clist = node_in_list(next_node, _olist), node_in_list(next_node, _clist)

            if _in_olist and _g_cost < next_node['g']:
                del _olist[next_node]

            if _in_clist and _g_cost < next_node['g']:
                del _clist[next_node['id']]

            if not _in_olist and not _in_clist:
                next_node['g'] = _g_cost
                next_node['h'] = distance_to_state(next_node['state'], path['goal'])
                next_node['f'] = next_node['g'] + next_node['h']
                next_node['p_id'] = node['id']

                _olist[next_node['id']] = next_node

        return []

