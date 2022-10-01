本项目主要用于研究类型检查器的实现与纯实现.

截至撰写本文档时, 本项目已完整实现了一个 `SystemF<:` 的 `typeof` 实现.

```py
from typeof import *

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
print(type_of([], zero))
# -> ∀X<:any.∀S<:#X.∀Z<:#X.(X -> #S) -> Z -> #Z
```