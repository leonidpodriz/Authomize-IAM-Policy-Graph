from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Iterable, List, Optional, Set, Tuple, TypeVar

from gcp.graph.edge import Edge
from gcp.graph.node import InnerNodeType, Node

NodeType = TypeVar('NodeType', bound=Node)
EdgeType = TypeVar('EdgeType', bound=Edge)

EdgeInnerType = Tuple[str, str]


@dataclass
class Graph(Generic[NodeType, EdgeType, InnerNodeType]):
    nodes: Set[NodeType] = field(default_factory=set)
    edges: Set[EdgeType] = field(default_factory=set)

    def get_node(self, search_node: NodeType) -> Optional[NodeType]:
        for node in self.nodes:
            if node == search_node:
                return node

        return None

    def get_or_add(self, search_node: NodeType) -> NodeType:
        node: Optional[NodeType] = self.get_node(search_node)

        if node is None:
            node = search_node
            self.nodes.add(node)

        return node

    def add_edge(self, edge: EdgeType) -> None:
        self.get_or_add(edge.previous)
        self.get_or_add(edge.next)
        self.edges.add(edge)

    def get_edges_by_types(self, *edges_types: EdgeInnerType) -> Iterable[EdgeType]:
        return filter(lambda edge: edge.type in edges_types, self.edges)

    @staticmethod
    def map_edge_to_previous(edge: Edge[Any]) -> NodeType:
        return edge.previous

    @staticmethod
    def map_edge_to_next(edge: Edge[Any]) -> NodeType:
        return edge.next

    @staticmethod
    def filter_edges_by_previous(node: Node[Any]) -> Callable[[EdgeType], bool]:
        def filter_func(edge: EdgeType) -> bool:
            return edge.previous == node

        return filter_func

    @staticmethod
    def filter_edges_by_next(node: Node[Any]) -> Callable[[EdgeType], bool]:
        def filter_func(edge: EdgeType) -> bool:
            return edge.next == node

        return filter_func

    def _get_of(
            self,
            node: Node,
            edges_type: Optional[EdgeInnerType] = None,
            up: bool = False,
            deep: bool = False
    ) -> Iterable[NodeType]:
        # Pay attention: it skips every child node of filtered by type edge:
        edges: Iterable[EdgeType] = self.get_edges_by_types(edges_type) if edges_type is not None else self.edges
        node_edges: Iterable[EdgeType] = filter(
            self.filter_edges_by_next(node) if up else self.filter_edges_by_previous(node), edges
        )
        found_nodes: List[NodeType] = list(
            map(self.map_edge_to_previous if up else self.map_edge_to_next, node_edges)
        )

        yield from found_nodes

        if deep:
            for __node in found_nodes:
                yield from self._get_of(__node, edges_type, up, deep)

    def get_parents_of(self, node: Node, edges_type: Optional[EdgeInnerType] = None) -> Iterable[NodeType]:
        return self._get_of(node, edges_type, up=True)

    def get_children_of(self, node: Node, edges_type: Optional[EdgeInnerType] = None) -> Iterable[NodeType]:
        return self._get_of(node, edges_type)

    def get_all_children_of(self, node: Node, edges_type: Optional[EdgeInnerType] = None) -> Iterable[NodeType]:
        return self._get_of(node, edges_type, deep=True)

    def get_all_parents_of(self, node: Node, edges_type: Optional[EdgeInnerType] = None) -> Iterable[NodeType]:
        return self._get_of(node, edges_type, up=True, deep=True)
