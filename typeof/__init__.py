from .main import type_of as type_of

from .types import (
    FArrow as FArrow,
    FTrue as FTrue,
    FFalse as FFalse,
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
    FTAbs as FTAbs,
    FTApp as FTApp,
    FTBool as FTBool,
    FTCond as FTCond,
    FTFix as FTFix,
    FTIsZero as FTIsZero,
    FTNat as FTNat,
    FTPredecessor as FTPredecessor,
    FTSuccessor as FTSuccessor,
    FTTypeAbs as FTTypeAbs,
    FTTypeApp as FTTypeApp,
    FTerm as FTerm,
    FTVar as FTVar,
)
