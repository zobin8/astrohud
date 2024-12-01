"""Models for horo endpoint"""

from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Dict


@dataclass
class Option:
    """Option for a setting"""
    value: str
    description: str

    @classmethod
    def make_options(cls, items: Dict[str, str]) -> List[Any]:
        """Construct a list of options from a value-description dict"""
        return [cls(value=v, description=d) for v, d in items.items()]
