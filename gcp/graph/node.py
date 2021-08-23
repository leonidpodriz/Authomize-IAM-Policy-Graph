from dataclasses import dataclass, field
from typing import Generic, Tuple, TypeVar

InnerNodeType = TypeVar('InnerNodeType', bound=str)


@dataclass(frozen=True)
class Node(Generic[InnerNodeType]):
    id: str
    type: InnerNodeType
    artefacts: Tuple[str, ...] = field(default_factory=tuple)

    def __str__(self):
        return self.id

    def __repr__(self):
        return 'Node{%s}' % self.id
