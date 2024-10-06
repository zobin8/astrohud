from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from dataclasses import dataclass

from astrohud.astro.enums import Sign
from astrohud.astro.enums import House


@dataclass
class RenderSettings:
    """Settings for drawing the horoscope"""

    asc_angle: float
    signs: List[Tuple[Sign, float]]
    cusps: List[Tuple[House, float]]


class UnionFind:
    parents: Dict[Any, Any]
    members: Dict[Any, set]

    def __init__(self) -> None:
        self.parents = dict()
        self.members = dict()

    def add(self, item: Any):
        if item not in self.parents:
            self.parents[item] = item
            self.members[item] = {item}

    def find(self, item: Any) -> Any:
        parent = self.parents.get(item, None)
        if parent is None or parent == item:
            return parent
        self.parents[item] = self.find(parent)
        return self.parents[item]
    
    def union(self, item1: Any, item2: Any):
        self.add(item1)
        self.add(item2)
        item1 = self.find(item1)
        item2 = self.find(item2)

        if item1 == item2:
            return
        
        if len(self.members[item1]) < len(self.members[item2]):
            item1, item2 = item2, item1

        self.parents[item2] = item1
        self.members[item1] = self.members[item1].union(self.members.pop(item2))
