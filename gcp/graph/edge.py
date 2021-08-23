from dataclasses import dataclass
from typing import Generic, Tuple, TypeVar

from gcp.graph.node import Node

NodeType = TypeVar('NodeType', bound=Node)


@dataclass(frozen=True)
class Edge(Generic[NodeType]):
    previous: NodeType
    next: NodeType

    @property
    def type(self) -> Tuple[str, str]:
        return self.previous.type, self.next.type
