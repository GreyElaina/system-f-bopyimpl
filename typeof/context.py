from dataclasses import dataclass
from typing import TypeAlias

from .types import FType


@dataclass(unsafe_hash=True)
class FTermBind:
    name: str
    term_type: FType


@dataclass(unsafe_hash=True)
class FTypeBind:
    name: str
    bound: FType


ContextBind = FTermBind | FTypeBind
TContext: TypeAlias = list[ContextBind]


def widen_ctx(context: TContext, binding: ContextBind):
    copied_context = context.copy()
    copied_context.append(binding)
    return copied_context
