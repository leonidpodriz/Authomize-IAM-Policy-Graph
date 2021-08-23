import json
from typing import Collection, List, Tuple

from gcp.policy.edge import GCPEdge
from gcp.policy.graph import GCPGraph
from gcp.policy.node import GCPNode
from gcp.policy.node_type import GCPNodeType
from gcp.utils import get_unique_identifier_from_name

ResourceNode = GCPNode
ResourceTypeNode = GCPNode
RoleNode = GCPNode
MemberNode = GCPNode
MemberPermissionData = Tuple[ResourceNode, ResourceTypeNode, RoleNode]


class PolicyManager:
    graph: GCPGraph = GCPGraph()

    def _get_resource_by_id_and_type(self, resource_id: str, _type: GCPNodeType) -> GCPNode:
        for node in self.graph.nodes:
            if node.id == resource_id and node.type == _type:
                return node

        raise KeyError(f'Node \'{resource_id}\' and type \'{_type}\' not found')

    def get_resource_by_id(self, resource_id: str) -> GCPNode:
        return self._get_resource_by_id_and_type(resource_id, GCPNodeType.resource)

    def get_member_by_id(self, member_id: str) -> GCPNode:
        return self._get_resource_by_id_and_type(member_id, GCPNodeType.member)

    def get_one_node_parent(self, node: GCPNode, _type: GCPNodeType) -> GCPNode:
        for node in self.graph.get_parents_of(node, (_type, node.type)):
            return node

        raise KeyError(f'Parent of {node} with type {_type} not found')

    def get_one_node_child(self, node: GCPNode, _type: GCPNodeType) -> GCPNode:
        for node in self.graph.get_children_of(node, (node.type, _type)):
            return node

        raise KeyError(f'Child of {node} with type {_type} not found')

    def get_one_resource_parent(self, node: GCPNode) -> GCPNode:
        return self.get_one_node_parent(node, GCPNodeType.resource)

    def get_resource_parents(self, resource: GCPNode) -> Tuple[ResourceNode, ...]:
        try:
            parent: GCPNode = self.get_one_resource_parent(resource)
        except KeyError:
            return tuple()

        return parent, *self.get_resource_parents(parent)

    def get_resource_path(self, resource: GCPNode) -> Tuple[str, ...]:
        return tuple(map(lambda r: r.id, self.get_resource_parents(resource)))

    def get_child_resources(self, node: ResourceNode) -> List[ResourceNode]:
        first_line_children = list(self.graph.get_children_of(node, (node.type, GCPNodeType.resource)))

        for child in first_line_children:
            first_line_children.extend(self.get_child_resources(child))

        return first_line_children

    def get_member_roles(self, node: MemberNode) -> Tuple[RoleNode, ...]:
        return tuple(self.graph.get_parents_of(node, (GCPNodeType.role, node.type)))

    def get_resource_type(self, node: ResourceNode) -> ResourceTypeNode:
        return self.get_one_node_child(node, GCPNodeType.resourceType)

    def get_all_members_permission(self, node: MemberNode) -> List[MemberPermissionData]:
        roles: Tuple[RoleNode, ...] = self.get_member_roles(node)
        permissions: List[MemberPermissionData] = list()

        for role in roles:
            artefact_resource_id: str = role.artefacts[0]
            resource: ResourceNode = self.get_resource_by_id(artefact_resource_id)
            child_resources: Collection[ResourceNode] = self.get_child_resources(resource)
            all_resources = [resource, *child_resources]

            for legacy_resource in all_resources:
                legacy_resource_type: ResourceTypeNode = self.get_resource_type(legacy_resource)
                permissions.append((legacy_resource, legacy_resource_type, role))

        return permissions

    def get_resource_roles(self, node: ResourceNode) -> Tuple[RoleNode, ...]:
        return tuple(self.graph.get_children_of(node, (node.type, GCPNodeType.role)))

    def get_role_members(self, node: RoleNode) -> Tuple[MemberNode, ...]:
        return tuple(self.graph.get_children_of(node, (node.type, GCPNodeType.member)))

    def get_resource_member_permissions(self, node: ResourceNode) -> List[Tuple[MemberNode, RoleNode]]:
        permissions: List[Tuple[MemberNode, RoleNode]] = list()
        parents_resources: Collection[ResourceNode] = self.get_resource_parents(node)
        all_resources = [node, *parents_resources]

        for resource in all_resources:
            for role in self.get_resource_roles(resource):
                for member in self.get_role_members(role):
                    permissions.append((member, role))

        return permissions

    @classmethod
    def from_file(cls, filepath: str) -> 'PolicyManager':
        manager = cls()

        with open(filepath) as gcp_policy_file:
            gcp_policy_data: List[dict] = json.load(gcp_policy_file)

        for resource in gcp_policy_data:
            name: str = resource.get('name', '')
            asset_type: str = resource.get('asset_type', '')
            ancestors: List[str] = resource.get('ancestors', list())
            unique_identifier: str = get_unique_identifier_from_name(name)

            resource_node: GCPNode = manager.graph.get_or_add(GCPNode(unique_identifier, GCPNodeType.resource))

            manager.graph.add_edge(
                GCPEdge(
                    resource_node,
                    GCPNode(asset_type, GCPNodeType.resourceType),
                )
            )

            if len(ancestors) > 1:
                previous_unique_identifier = ancestors[1]
                manager.graph.add_edge(
                    GCPEdge(
                        GCPNode(previous_unique_identifier, GCPNodeType.resource),
                        resource_node,
                    )
                )

            iam_policy: dict = resource.get('iam_policy', dict())
            bindings: List[dict] = iam_policy.get('bindings', list())

            for bind in bindings:
                role: str = bind.get('role', '')
                members: List[str] = bind.get('members', list())
                role_node: GCPNode = manager.graph.get_or_add(
                    GCPNode(role, GCPNodeType.role, artefacts=(unique_identifier,))
                )
                manager.graph.add_edge(GCPEdge(resource_node, role_node))

                for member in members:
                    manager.graph.add_edge(
                        GCPEdge(
                            role_node,
                            GCPNode(member, GCPNodeType.member),
                        )
                    )

        return manager
