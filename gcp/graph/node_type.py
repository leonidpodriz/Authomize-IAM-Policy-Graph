from enum import Enum


class NodeType(str, Enum):
    resource = 'resource'
    resourceType = 'resourceType'
    member = 'member'
    role = 'role'
