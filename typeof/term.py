from dataclasses import dataclass

from .types import FType


@dataclass(unsafe_hash=True)
class FTerm:
    pass


@dataclass(unsafe_hash=True)
class FTVar(FTerm):
    name: str


@dataclass(unsafe_hash=True)
class FTAbs(FTerm):
    generic: str
    generic_type: FType
    body: FTerm


@dataclass(unsafe_hash=True)
class FTApp(FTerm):
    func: FTerm
    arg: FTerm


@dataclass(unsafe_hash=True)
class FTBool(FTerm):
    value: bool


@dataclass(unsafe_hash=True)
class FTNat(FTerm):
    value: int


@dataclass(unsafe_hash=True)
class FTSuccessor(FTerm):
    arg: FTerm


@dataclass(unsafe_hash=True)
class FTPredecessor(FTerm):
    arg: FTerm


@dataclass(unsafe_hash=True)
class FTIsZero(FTerm):
    arg: FTerm


@dataclass(unsafe_hash=True)
class FTCond(FTerm):
    cond: FTerm
    then: FTerm
    else_: FTerm


@dataclass(unsafe_hash=True)
class FTFix(FTerm):
    arg: FTerm


@dataclass(unsafe_hash=True)
class FTTypeAbs(FTerm):
    generic: str
    bound: FType
    body: FTerm


@dataclass(unsafe_hash=True)
class FTTypeApp(FTerm):
    func: FTerm
    arg: FType
