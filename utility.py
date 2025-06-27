import yaml

def findProbe (cel_bodies):
    bodies = {}
    for body_index in range(0, len(cel_bodies['bodies'])):
        for _body, _param in cel_bodies['bodies'][body_index].items():
            if 'probe' not in _param:
                _param['probe'] = 'False'
            else:
                bodies[_body] = _body.lower()
    return bodies


def readConfig(filename):
    _bodies = None
    with open(filename) as stream:
        try:
            _bodies = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return _bodies