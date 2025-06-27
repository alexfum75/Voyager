def findComet (cel_bodies):
    body = ''
    body_lower_name = ''
    found_target = False
    for body_index in range(0, len(cel_bodies['bodies'])):
        for _body, _param in cel_bodies['bodies'][body_index].items():
            if 'comet' not in _param:
                _param['comet'] = 'False'
            body = _body
            body_lower_name = _body.lower()
            found_target = True
            break
        if found_target:
            break
    return body, body_lower_name


def readConfig(filename):
    _bodies = None
    with open(filename) as stream:
        try:
            _bodies = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return _bodies