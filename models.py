class Policy:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Route:
    def __init__(self, id, path, method, target_url, policy_id=None, policy_name=None):
        self.id = id
        self.path = path
        self.method = method
        self.target_url = target_url
        self.policy_id = policy_id
        self.policy_name = policy_name
