from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class FType:
    def __repr__(self):
        if self is FBool:
            return "bool"
        elif self is FNat:
            return "nat"
        elif self is FTop:
            return "any"
        elif self is FBottom:
            return "never"


FBool = FType()
FNat = FType()
FTop = FType()
FBottom = FType()


@dataclass(unsafe_hash=True)
class FUnion(FType):
    members: list[FType]


@dataclass(unsafe_hash=True)
class FIntersection(FType):
    members: list[FType]


@dataclass(unsafe_hash=True)
class FVar(FType):
    name: str
    generic: bool

    def __repr__(self):
        return f"#{self.name}"


@dataclass(unsafe_hash=True)
class FArrow(FType):
    domain: FType
    result: FType

    def __repr__(self):
        match (self.domain, self.result):
            case (FVar(domain), result):
                return f"{domain} -> {repr(result)}"
            case (domain, result):
                return f"({repr(domain)}) -> {repr(result)}"


@dataclass(unsafe_hash=True)
class FForAll(FType):
    generic: str
    bound: FType
    body: FType

    def __repr__(self):
        return f"∀{self.generic}<:{repr(self.bound)}.{repr(self.body)}"


@dataclass
class FStructShape(FType):
    shape: dict[str, FType]

    def __hash__(self) -> int:
        return hash(hash("FStructShape") + hash(tuple(self.shape.items())))


# TODO: kinding type, type operator to support generic in a better way.
