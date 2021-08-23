from uuid import uuid4

from gcp.policy.edge import GCPEdge
from gcp.policy.graph import GCPGraph
from gcp.policy.node import GCPNode
from gcp.policy.node_type import GCPNodeType

node_1 = GCPNode('1', GCPNodeType.resource)
node_2 = GCPNode('2', GCPNodeType.resourceType)
graph = GCPGraph(nodes={node_1, node_2})


def test_graph_get_node():
    assert graph.get_node(GCPNode('1', GCPNodeType.resource)) is node_1
    assert graph.get_node(GCPNode('2', GCPNodeType.resourceType)) is node_2


def test_graph_get_or_add():
    assert graph.get_or_add(GCPNode('1', GCPNodeType.resource)) is node_1


def test_graph_add_edge():
    nodes_len_before: int = len(graph.nodes)
    edges_len_before: int = len(graph.edges)
    graph.add_edge(
        GCPEdge(
            GCPNode('1', GCPNodeType.resource),
            GCPNode('4', GCPNodeType.resource),
        )
    )

    nodes_len_after: int = len(graph.nodes)
    edges_len_after: int = len(graph.edges)

    assert nodes_len_after == nodes_len_before + 1
    assert edges_len_after == edges_len_before + 1


def test_graph_get_edges_by_types():
    resource_to_resource_type = (GCPNodeType.resource, GCPNodeType.resourceType)
    count_before_added_edge = len(list(graph.get_edges_by_types(resource_to_resource_type)))
    graph.add_edge(
        GCPEdge(
            GCPNode('1', GCPNodeType.resource),
            GCPNode('5', GCPNodeType.resourceType),
        )
    )
    count_after_added_edge = len(list(graph.get_edges_by_types(resource_to_resource_type)))

    assert count_after_added_edge == count_before_added_edge + 1


def test_graph_get_all_children_of_and_get_all_parents_of():
    node_3 = GCPNode(str(uuid4()), GCPNodeType.resource)
    node_4 = GCPNode(str(uuid4()), GCPNodeType.resource)
    node_5 = GCPNode(str(uuid4()), GCPNodeType.resource)
    node_6 = GCPNode(str(uuid4()), GCPNodeType.resource)

    graph.add_edge(GCPEdge(node_3, node_4))
    graph.add_edge(GCPEdge(node_3, node_5))
    graph.add_edge(GCPEdge(node_5, node_6))

    children_nodes = list(graph.get_all_children_of(node_3))

    assert node_4 in children_nodes
    assert node_5 in children_nodes
    assert node_6 in children_nodes

    parent_nodes = list(graph.get_all_parents_of(node_6))

    assert node_3 in parent_nodes
    assert node_5 in parent_nodes
