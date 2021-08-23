from enum import Enum


class GCPNodeType(str, Enum):
    resource = 'resource'
    resourceType = 'resourceType'
    member = 'member'
    role = 'role'
