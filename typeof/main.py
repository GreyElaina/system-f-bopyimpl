from typeof.util import unique_string
from .error import TypeMismatchError, UnknownBindingError
from .types import (
    FArrow,
    FBool,
    FBottom,
    FFalse,
    FForAll,
    FIntersection,
    FNat,
    FTop,
    FTrue,
    FType,
    FUnion,
    FVar,
)
from .term import (
    FTAbs,
    FTApp,
    FTBool,
    FTCond,
    FTFix,
    FTIsZero,
    FTNat,
    FTPredecessor,
    FTSuccessor,
    FTTypeAbs,
    FTTypeApp,
    FTerm,
    FTVar,
)
from .context import FTermBind, FTypeBind, TContext, widen_ctx


def check_nat(context: TContext, term: FTerm):
    if (t := type_of(context, term)) is FNat:
        return FBool
    raise TypeMismatchError(f"expected nat, got {repr(t)}")


def find_binding(context: TContext, name: str):
    for i in context:
        if i.name == name:
            return i


def find_first_non_monotype(context: TContext, input: FType) -> FType | None:
    if isinstance(input, FVar) and input.generic:
        for i in context:
            if isinstance(i, FTypeBind) and i.name == input.name:
                if isinstance(i.bound, FVar):
                    return find_first_non_monotype(context, i.bound)
                return i.bound
    return input


def get_free_variables(t: FType) -> set[str]:
    match t:
        case FVar(name):
            return {name}
        case FUnion(left, right):
            return get_free_variables(left) | get_free_variables(right)
        case FIntersection(left, right):
            return get_free_variables(left) | get_free_variables(right)
        case FArrow(domain, result):
            return get_free_variables(domain) | get_free_variables(result)
        case FForAll(generic, bound, body):
            res = get_free_variables(bound) | get_free_variables(body)
            res.discard(generic)
            return res
        case _:
            return set()


def substitude_type(t: FType, name: str, replace_to: FType) -> FType:
    match t:
        case FVar(n):
            if name == n:
                return replace_to
            return t
        case FUnion(left, right):
            return FUnion(
                substitude_type(left, name, replace_to),
                substitude_type(right, name, replace_to),
            )
        case FIntersection(left, right):
            return FIntersection(
                substitude_type(left, name, replace_to),
                substitude_type(right, name, replace_to),
            )
        case FArrow(domain, result):
            return FArrow(
                substitude_type(domain, name, replace_to),
                substitude_type(result, name, replace_to),
            )
        case FForAll(generic, bound, body):
            if name == generic:
                return t

            if generic in get_free_variables(replace_to):
                new_generic = unique_string(
                    get_free_variables(replace_to) | get_free_variables(body)
                )
                new_body = substitude_type(body, generic, FVar(new_generic, True))
                return FForAll(
                    new_generic,
                    substitude_type(bound, name, replace_to),
                    substitude_type(new_body, name, replace_to)
                )

            return FForAll(
                generic,
                substitude_type(bound, name, replace_to),
                substitude_type(body, name, replace_to)
            )
        case _:
            return t


def is_subtype(context: TContext, left: FType, right: FType) -> bool:
    print(f"judging ({left}) <: ({right}), in {context}")
    match (left, right):
        case (_, _) if left == right:
            return True
        case (_, _) if right == FTop:
            return True
        case (_, _) if right == FBottom:
            return False
        case (FVar() as left_var, _):
            binding = find_binding(context, left_var.name)
            if isinstance(binding, FTypeBind):
                return is_subtype(context, binding.bound, right)
            return False
        case (
            FArrow(domain=left_domain, result=left_result),
            FArrow(domain=right_domain, result=right_result),
        ):
            return is_subtype(context, right_domain, left_domain) and is_subtype(
                context, left_result, right_result
            )
        case (
            FForAll(left_generic, left_bound, left_body),
            FForAll(right_generic, right_bound, right_body),
        ):
            generic_compliant = is_subtype(context, right_bound, left_bound)
            new_generic_name = unique_string(
                get_free_variables(left_body) | get_free_variables(right_body) | {i.name for i in context if isinstance(i, FTypeBind)}
            )
            new_left_body = substitude_type(
                left_body, left_generic, FVar(new_generic_name, True)
            )
            new_right_body = substitude_type(
                right_body, right_generic, FVar(new_generic_name, True)
            )
            new_context = widen_ctx(context, FTypeBind(new_generic_name, right_bound))
            return generic_compliant and is_subtype(
                new_context, new_left_body, new_right_body
            )
        case (_, FUnion(union_left, union_right)):
            return is_subtype(context, left, union_left) or is_subtype(
                context, right, union_right
            )
        case (_, FIntersection(intersection_left, intersection_right)):
            return is_subtype(context, left, intersection_left) and is_subtype(
                context, right, intersection_right
            )
        case _:
            return False

def type_of(context: TContext, term: FTerm) -> FType:
    match term:
        case FTVar(name):
            binding = find_binding(context, name)
            if binding is None or not isinstance(binding, FTermBind):
                raise TypeMismatchError(
                    f"cannot find variable of name {name} in context"
                )
            return binding.term_type
        case FTAbs(generic, generic_type, body):
            return FArrow(
                generic_type,
                type_of(widen_ctx(context, FTermBind(generic, generic_type)), body),
            )
        case FTApp(func, arg):
            func_type = type_of(context, func)
            arg_type = type_of(context, arg)

            func_type_infered = find_first_non_monotype(context, func_type)
            if isinstance(func_type_infered, FArrow):
                if is_subtype(context, arg_type, func_type_infered.domain):
                    return func_type_infered.result
                raise TypeMismatchError(
                    f"expected argument type to be a subtype of {func_type_infered.domain}, got {arg_type}"
                )
            raise TypeMismatchError(f"expected arrow type, got {func_type_infered}")
        case FTTypeAbs(generic, bound, body):
            return FForAll(
                generic,
                bound,
                type_of(widen_ctx(context, FTypeBind(generic, bound)), body),
            )
        case FTTypeApp(abs_, arg):
            match find_first_non_monotype(context, type_of(context, abs_)):
                case FForAll(generic, bound, body):
                    if is_subtype(context, arg, bound):
                        return substitude_type(body, generic, arg)
                    raise TypeMismatchError(
                        f"expected argument type to be a subtype of {bound}, got {arg}"
                    )
                case t:
                    raise TypeMismatchError(f"expected generic (forall) type, got {t}")
        case FTCond(cond, then_branch, else_branch):
            cond_type = type_of(context, cond)
            then_branch_type = type_of(context, then_branch)
            else_branch_type = type_of(context, else_branch)
            if cond_type is FTrue:
                return then_branch_type
            elif cond_type is FFalse:
                return else_branch_type
            elif cond_type is FBool:
                return FUnion(then_branch_type, else_branch_type)
            raise TypeMismatchError(f"expected boolean condition, got {cond_type}")
        case FTBool(True):
            return FTrue
        case FTBool(False):
            return FFalse
        case FTBool():
            return FBool
        case FTNat():
            return FNat
        case FTIsZero(arg):
            return check_nat(context, arg)
        case FTSuccessor(arg) | FTPredecessor(arg):
            check_nat(context, arg)
            return FNat
        case FTFix(arg):
            arg_type = type_of(context, arg)
            if isinstance(arg, FArrow) and arg.domain == arg.result:
                return arg.domain
            raise TypeMismatchError(
                f"the type of a fix operator must be a function type, which, accepts a function type, and returns an identical function type"
            )
        case _:
            raise TypeError(f"Unknown type: {term}")
