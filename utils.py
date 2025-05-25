import os

POLICY_DIR = './policies'

def load_policy_code(policy_name):
    name = policy_name[0]
    policy_path = os.path.join(POLICY_DIR, f"{name}.py")
    if not os.path.isfile(policy_path):
        raise FileNotFoundError(f"Policy '{policy_name}.py' not found")
    with open(policy_path, 'r') as f:
        return f.read()

def exec_policy(policy_code, request, reject):
    exec_globals = {'request': request, 'reject': reject}
    exec(policy_code, exec_globals)
