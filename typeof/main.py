from functools import reduce
from .error import TypeMismatchError, UnknownBindingError
from .types import (
    FArrow,
    FBool,
    FBottom,
    FForAll,
    FIntersection,
    FNat,
    FStructShape,
    FTop,
    FType,
    FUnion,
    FVar,
)
from .term import (
    Abstraction,
    Any,
    Application,
    Boolean,
    Equals,
    If,
    FTFix,
    FTIsZero,
    Intersection,
    LiteralValue,
    Nat,
    FTPredecessor,
    StructShape,
    SubtypeOf,
    FTSuccessor,
    Never,
    FTTypeAbs,
    FTTypeApp,
    Exp,
    Union,
    Variable,
)
from .context import (
    ContextBind,
    FExpAlias,
    FTermBind,
    FTypeBind,
    TContext,
    widen_ctx,
    find_binding,
)
from .util import unique_string


def check_nat(context: TContext, term: Exp):
    if (t := type_of(context, term)) is FNat:
        return FBool
    raise TypeMismatchError(f"expected nat, got {repr(t)}")


def find_first_non_monotype(context: TContext, input: FType) -> FType | None:
    if isinstance(input, FVar) and input.generic:
        for i in context:
            if isinstance(i, FTypeBind) and i.name == input.name:
                if isinstance(i.bound, FVar):
                    return find_first_non_monotype(context, i.bound)
                return i.bound
    return input


def get_variable_expalias(context: TContext, var_name: str) -> Exp | None:
    for i in context:
        if i.name == var_name and isinstance(i, FExpAlias):
            return i.exp


def get_free_variables(t: FType) -> set[str]:
    match t:
        case FVar(name):
            return {name}
        case FUnion(members):
            return reduce(set.union, [get_free_variables(mem) for mem in members])
        case FIntersection(members):
            return reduce(set.union, [get_free_variables(mem) for mem in members])
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
        case FUnion(members):
            return FUnion([
                substitude_type(i, name, replace_to)
            for i in members])
        case FIntersection(members):
            return FIntersection([
                substitude_type(i, name, replace_to)
            for i in members])
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
                    substitude_type(new_body, name, replace_to),
                )

            return FForAll(
                generic,
                substitude_type(bound, name, replace_to),
                substitude_type(body, name, replace_to),
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
        case (LiteralValue(left_value), _):
            return is_subtype(context, type_of(context, left_value), right)
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
                get_free_variables(left_body)
                | get_free_variables(right_body)
                | {i.name for i in context if isinstance(i, FTypeBind)}
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
        case (FStructShape(left_shape), FStructShape(right_shape)):
            if not set(left_shape.keys()).issuperset(right_shape.keys()):
                return False
            for label, anno in left_shape.items():
                if label not in right_shape:
                    continue
                if not is_subtype(context, anno, right_shape[label]):
                    return False
            return True
        case (_, FUnion(members)):
            for member in members:
                if is_subtype(context, left, member):
                    return True
            return False
        case (_, FIntersection(members)):
            for member in members:
                if not is_subtype(context, left, member):
                    return False
            return True
        case _:
            return False


def is_conclict(context: TContext, extern_binding: ContextBind) -> bool:
    existed_binding = find_binding(context, extern_binding.name)
    if existed_binding is None:
        return False
    match existed_binding, extern_binding:
        case (FTypeBind(_, existed), FTypeBind(_, extern)):
            return is_subtype(context, extern, existed)
        case (FTermBind(_, existed), FTermBind(_, extern)):
            return is_subtype(
                context, extern, existed
            )
        case _:
            return False


def type_of(context: TContext, term: Exp) -> FType:
    match term:
        case Variable(name):
            binding = find_binding(context, name)
            if binding is None or not isinstance(binding, FTermBind):
                raise TypeMismatchError(
                    f"cannot find variable of name {name} in context"
                )
            return binding.term_type
        case Abstraction(generic, generic_type, body):
            return FArrow(
                generic_type,
                type_of(
                    widen_ctx(context, FTermBind(generic, generic_type)), body
                ),
            )
        case Application(func, arg):
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
        case If(_, then_branch, else_branch):
            then_branch_type = type_of(context, then_branch)
            else_branch_type = type_of(context, else_branch)
            return FUnion([then_branch_type, else_branch_type])
        case Union(members):
            return FUnion([type_of(context, evaluate(context, i)) for i in members])
        case Boolean():
            return FBool
        case Nat():
            return FNat
        case LiteralValue(value):
            return type_of(context, value)
        case x if x is Never:
            return FBottom
        case x if x is Any:
            return FTop
        case FTIsZero(arg):
            return check_nat(context, arg)
        case FTSuccessor(arg) | FTPredecessor(arg):
            check_nat(context, arg)
            return FNat
        case StructShape(shape):
            return FStructShape({k: type_of(context, v) for k, v in shape.items()})
        case FTFix(arg):
            arg_type = type_of(context, arg)
            if isinstance(arg, FArrow) and arg.domain == arg.result:
                return arg.domain
            raise TypeMismatchError(
                f"the type of a fix operator must be a function type, which, accepts a function type, and returns an identical function type"
            )
        case _:
            raise TypeError(f"Unknown type: {term}")


def kinding_of(context: TContext, ftype: FType) -> ...:
    ...


def evaluate(context: TContext, term: Exp) -> Exp:
    match term:
        case Variable(name):
            if (var_term := get_variable_expalias(context, name)) is None:
                raise UnknownBindingError(f"cannot found '{name}' in current context")
            return var_term
        case If(cond, then, else_):
            cond_eval_result = evaluate(context, cond)
            match cond_eval_result:
                case Boolean(True):
                    return evaluate(context, then)
                case Boolean(False):
                    return evaluate(context, else_)
                case _:
                    raise TypeMismatchError(
                        f"assert a boolean but received a {repr(cond_eval_result)}"
                    )
        case SubtypeOf(left, right):
            left_eval_result = evaluate(context, left)
            right_eval_result = evaluate(context, right)
            return Boolean(
                is_subtype(
                    context,
                    type_of(context, left_eval_result),
                    type_of(context, right_eval_result),
                )
            )
        case Equals(left, right):
            return Boolean(evaluate(context, left) == evaluate(context, right))
        case Union(members):
            return Union(*[evaluate(context, i) for i in members])
        case Intersection(members):
            return Intersection(*[evaluate(context, i) for i in members])
        case _:
            return term
