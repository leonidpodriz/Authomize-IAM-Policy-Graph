from pprint import pprint

from gcp.policy_manager import PolicyManager

manager = PolicyManager.from_file('tests/data.json')
print(manager.graph)

resource = manager.get_resource_by_id('folders/837642324986')
path = manager.get_resource_path(resource)
print(path)

member = manager.get_member_by_id('user:ron@test.authomize.com')
permissions = manager.get_all_members_permission(member)
pprint(permissions)

root_resource = manager.get_resource_by_id('organizations/1066060271767')
root_children = manager.get_child_resources(root_resource)
print(root_children)

permissions_to_resource = manager.get_resource_member_permissions(root_resource)
print(permissions_to_resource)
