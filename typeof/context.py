from dataclasses import dataclass
from typing import TypeAlias

from typeof.term import Exp

from .types import FType


@dataclass(unsafe_hash=True)
class FTermBind:
    name: str
    term_type: FType


@dataclass(unsafe_hash=True)
class FExpAlias:
    name: str
    exp: Exp


@dataclass(unsafe_hash=True)
class FTypeBind:
    name: str
    bound: FType


ContextBind = FTermBind | FTypeBind | FExpAlias
TContext: TypeAlias = list[ContextBind]


def widen_ctx(context: TContext, binding: ContextBind):
    copied_context = context.copy()
    copied_context.append(binding)
    return copied_context


def find_binding(context: TContext, name: str):
    for i in context:
        if i.name == name:
            return i
