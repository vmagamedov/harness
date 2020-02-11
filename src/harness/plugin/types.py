from typing import Collection
from dataclasses import dataclass


@dataclass
class WireIn:
    name: str
    path: str


@dataclass
class WireOut:
    name: str
    path: str


@dataclass
class Context:
    proto_file: str
    inputs: Collection[WireIn]
    outputs: Collection[WireOut]


@dataclass
class OutputFile:
    name: str
    content: str
