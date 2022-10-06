from typeof import *
from typeof.context import FExpAlias, FTermBind, FTypeBind, TContext
from typeof.main import evaluate, get_free_variables, is_subtype
from typeof.term import Any, BoundsOf, StructShape, SubtypeOf, Never
from typeof.util import unique_string

# zero = FForAll("X", FTop, FForAll("S"))
b = If(
    Application(Abstraction("X", FNat, Boolean(False)), Nat(123)),
    Nat(4),
    Boolean(True),
)
zero = FTTypeAbs(
    "X",
    FTop,
    FTTypeAbs(
        "S",
        FVar("X", True),
        FTTypeAbs(
            "Z",
            FVar("X", True),
            Abstraction(
                "x",
                FArrow(FVar("X", True), FVar("S", True)),
                Abstraction("z", FVar("Z", True), Variable("z")),
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

ctx: TContext = [
    FExpAlias("T", Boolean(False))
]
cond = SubtypeOf(left=StructShape({"a": Boolean(True)}), right=Any)
t = If(cond, Nat(114514), Nat(45234523452345))
# => StructShape({"a": Boolean(True)}) <: Any ? 114514 : Nat(45234523452345)

print(evaluate(ctx, t))
