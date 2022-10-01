from typeof import *

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
fbool = FTBool(False)
a = type_of([], b)
print(a)