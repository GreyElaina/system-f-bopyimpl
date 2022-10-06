from .main import type_of as type_of

from .types import (
    FArrow as FArrow,
    FBool as FBool,
    FBottom as FBottom,
    FForAll as FForAll,
    FIntersection as FIntersection,
    FNat as FNat,
    FTop as FTop,
    FType as FType,
    FUnion as FUnion,
    FVar as FVar,
)
from .term import (
    Abstraction as Abstraction,
    Application as Application,
    Boolean as Boolean,
    If as If,
    FTFix as FTFix,
    FTIsZero as FTIsZero,
    Nat as Nat,
    FTPredecessor as FTPredecessor,
    FTSuccessor as FTSuccessor,
    FTTypeAbs as FTTypeAbs,
    FTTypeApp as FTTypeApp,
    Exp as Exp,
    Variable as Variable,
)
