from dataclasses import dataclass

from .types import FType


@dataclass(unsafe_hash=True)
class Exp:
    pass


@dataclass(unsafe_hash=True)
class Variable(Exp):
    name: str


@dataclass(unsafe_hash=True)
class Abstraction(Exp):
    generic: str
    generic_type: FType
    body: Exp


@dataclass(unsafe_hash=True)
class Application(Exp):
    func: Exp
    arg: Exp


@dataclass(unsafe_hash=True)
class Boolean(Exp):
    value: bool


@dataclass(unsafe_hash=True)
class Nat(Exp):
    value: int


@dataclass(unsafe_hash=True)
class FTSuccessor(Exp):
    arg: Exp


@dataclass(unsafe_hash=True)
class FTPredecessor(Exp):
    arg: Exp


@dataclass(unsafe_hash=True)
class FTIsZero(Exp):
    arg: Exp


@dataclass(unsafe_hash=True)
class If(Exp):
    condition: Exp
    then: Exp
    else_: Exp


@dataclass(unsafe_hash=True)
class FTFix(Exp):
    arg: Exp


@dataclass(unsafe_hash=True)
class FTTypeAbs(Exp):
    generic: str
    bound: FType
    body: Exp


@dataclass(unsafe_hash=True)
class FTTypeApp(Exp):
    func: Exp
    arg: FType


@dataclass
class StructShape(Exp):
    shape: dict[str, Exp]

    def __hash__(self) -> int:
        return hash(hash("FTStructShape") + hash(tuple(self.shape.items())))

Any = Exp()
Never = Exp()


@dataclass
class LiteralValue(Exp):
    value: Exp

@dataclass
class SubtypeOf(Exp):
    left: Exp
    right: Exp

@dataclass
class Equals(Exp):
    left: Exp
    right: Exp

@dataclass
class Union(Exp):
    members: list[Exp]

    def __init__(self, *members: Exp):
        self.members = list(members)

@dataclass
class Intersection(Exp):
    members: list[Exp]

    def __init__(self, *members: Exp):
        self.members = list(members)

@dataclass
class Sequence(Exp):
    members: list[Exp]

    def __init__(self, *members: Exp):
        self.members = list(members)
