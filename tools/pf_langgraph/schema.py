from typing import Any, Dict, List, TypedDict


class PFNode(TypedDict):
    id: str
    kind: str  # http_call | branch
    config: Dict[str, Any]


class PFSpec(TypedDict):
    version: int
    name: str
    description: str
    inputs: Dict[str, Any]
    nodes: List[PFNode]
    edges: List[Dict[str, str]]
    outputs: Dict[str, Any]


