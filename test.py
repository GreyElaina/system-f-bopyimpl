from typeof import *
from typeof.context import FTypeBind, TContext
from typeof.main import get_free_variables, is_subtype
from typeof.term import FTStructShape
from typeof.util import unique_string

# zero = FForAll("X", FTop, FForAll("S"))
b = FTCond(FTApp(FTAbs("X", FNat, FTBool(False)), FTNat(123)), FTNat(4), FTBool(True))
zero = FTTypeAbs(
    "X",
    FTop,
    FTTypeAbs(
        "S",
        FVar("X", True),
        FTTypeAbs(
            "Z",
            FVar("X", True),
            FTAbs(
                "x",
                FArrow(FVar("X", True), FVar("S", True)),
                FTAbs("z", FVar("Z", True), FTVar("z")),
            ),
        ),
    ),
)

"""
def neg_type(ty: FType):
    print(get_free_variables(ty))
    name = unique_string(get_free_variables(ty))
    return FForAll(name, ty, FVar(name, True))

type_t = FForAll("X", FTop, neg_type(
    FForAll("Y", FVar("X", True), neg_type(FVar("Y", True)))
))

ctx: TContext = [
    FTypeBind("X0", type_t)
]

print(is_subtype(
    ctx, 
    FVar("X0", True),
    FForAll("X1", FVar("X0", True), neg_type(FVar("X1", True)))
))
"""

print(type_of([], zero))
