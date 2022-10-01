// @author: dylech30th

// ReSharper disable MemberCanBePrivate.Global
// ReSharper disable UnusedType.Global
// ReSharper disable ClassNeverInstantiated.Global
// ReSharper disable ParameterTypeCanBeEnumerable.Local

namespace CSharpCompanion;

using SystemFSubContext = List<SystemFSubContextBinding>;

public class TypeMismatchException : Exception
{
    public TypeMismatchException(string? message) : base(message) { }
}

public abstract record SystemFSubType
{
    public static readonly BoolPrimitive BoolType = new();
    public static readonly NatPrimitive NatType = new();
    public static readonly Top TopType = new();
    public static readonly Bottom BottomType = new();

    public record BoolPrimitive : SystemFSubType;
    public record NatPrimitive : SystemFSubType;
    public record Top : SystemFSubType;
    public record Bottom : SystemFSubType;
    public record Union(SystemFSubType Left, SystemFSubType Right) : SystemFSubType;
    public record Intersect(SystemFSubType Left, SystemFSubType Right) : SystemFSubType;
    public record Variable(string Name, bool IsBinder) : SystemFSubType;
    public record Arrow(SystemFSubType Domain, SystemFSubType Result) : SystemFSubType;
    public record Forall(string Binder, SystemFSubType Bound, SystemFSubType Body) : SystemFSubType;

    public override string ToString()
    {
        static string Aux(SystemFSubType ty)
        {
            return ty switch
            {
                BoolPrimitive => "bool",
                NatPrimitive => "nat",
                Top => "any",
                Bottom => "never",
                Union(var lhs, var rhs) => (lhs, rhs) switch
                {
                    (Variable, Variable) => $"{Aux(lhs)} | {Aux(rhs)}",
                    (Variable, _) => $"{Aux(lhs)} | ({Aux(rhs)})",
                    (_, Variable) => $"({Aux(lhs)}) | {Aux(rhs)}",
                    _ => $"({Aux(lhs)}) | ({Aux(rhs)})"
                },
                Intersect(var lhs, var rhs) => (lhs, rhs) switch
                {
                    (Variable, Variable) => $"{Aux(lhs)} & {Aux(rhs)}",
                    (Variable, _) => $"{Aux(lhs)} & ({Aux(rhs)})",
                    (_, Variable) => $"({Aux(lhs)}) & {Aux(rhs)}",
                    _ => $"({Aux(lhs)}) & ({Aux(rhs)})"
                },
                Variable(var name, _) => name,
                Arrow(var domain, var result) => (domain, result) switch
                {
                    (Variable, _) => $"{Aux(domain)} -> {Aux(result)}",
                    _ => $"({Aux(domain)}) -> {Aux(result)}"
                },
                Forall(var binder, var bound, var body) => $"∀{binder}<:{Aux(bound)}.{Aux(body)}",
                _ => throw new ArgumentOutOfRangeException(nameof(ty), ty, null)
            };
        }

        return Aux(this);
    }
}

public abstract record SystemFSubTerm
{
    public record Variable(string Name) : SystemFSubTerm;
    public record Abstraction(string Binder, SystemFSubType BinderType, SystemFSubTerm Body) : SystemFSubTerm;
    public record Application(SystemFSubTerm Function, SystemFSubTerm Argument) : SystemFSubTerm;
    public record BoolLiteral(bool Value) : SystemFSubTerm;
    public record NatLiteral(int Value) : SystemFSubTerm;
    public record Successor(SystemFSubTerm Argument) : SystemFSubTerm;
    public record Predecessor(SystemFSubTerm Argument) : SystemFSubTerm;
    public record IsZero(SystemFSubTerm Argument) : SystemFSubTerm;
    public record Conditional(SystemFSubTerm Condition, SystemFSubTerm Then, SystemFSubTerm Else) : SystemFSubTerm;
    public record Fix(SystemFSubTerm Argument) : SystemFSubTerm;
    public record TypeAbstraction(string Binder, SystemFSubType Bound, SystemFSubTerm Body) : SystemFSubTerm;
    public record TypeApplication(SystemFSubTerm Function, SystemFSubType Argument) : SystemFSubTerm;
}

public abstract record SystemFSubContextBinding
{
    public record VTermBinding(string Name, SystemFSubType TermType) : SystemFSubContextBinding;
    public record VTypeBinding(string Name, SystemFSubType Bound) : SystemFSubContextBinding;
}

public static class UniqueString
{
    public static Func<ISet<string>, string> Generator()
    {
        var counter = 0;
        return excludes =>
        {
            string Candidate() => $"X{counter}";
            while (excludes.Contains(Candidate())) counter++;
            return Candidate();
        };
    }
}

public static class SystemFSubTypeChecker
{
    private static class Set
    {
        public static ISet<T> Singleton<T>(T item) => new HashSet<T>(new[] { item });
        public static ISet<T> Union<T>(IEnumerable<T> set, IEnumerable<T> other) => new HashSet<T>(set.Concat(other));
        public static ISet<T> BigUnion<T>(params IEnumerable<T>[] sets) => new HashSet<T>(sets.SelectMany(Function.Identity));
        public static ISet<T> OfIter<T>(IEnumerable<T> enumerable) => new HashSet<T>(enumerable);
        public static ISet<T> OfIter<T>(params T[] enumerable) => new HashSet<T>(enumerable);
        public static ISet<T> Empty<T>() => new HashSet<T>();
    }

    private static class Function
    {
        public static T Identity<T>(T value) => value;

        public static T Block<T>(Func<T> block) => block();
    }
    
    private static readonly Func<ISet<string>, string> UniqueStringGenerator = UniqueString.Generator();

    static SystemFSubTypeChecker()
    {
    }

    private static SystemFSubContext WidenContext(SystemFSubContext context, SystemFSubContextBinding binding)
        => context.Append(binding).ToList();
    
    private static IEnumerable<string> Fv(SystemFSubTerm term)
    {
        return term switch
        {
            SystemFSubTerm.Variable(var name) => Set.Singleton(name),
            SystemFSubTerm.Abstraction(var binder, _, var body) => Fv(body).Where(i => i != binder),
            SystemFSubTerm.Application(var function, var argument) => Set.Union(Fv(function), Fv(argument)),
            SystemFSubTerm.Successor(var argument) => Fv(argument),
            SystemFSubTerm.Predecessor(var argument) => Fv(argument),
            SystemFSubTerm.IsZero(var argument) => Fv(argument),
            SystemFSubTerm.Conditional(var condition, var then, var @else) => Set.BigUnion(Fv(condition), Fv(then), Fv(@else)),
            SystemFSubTerm.TypeAbstraction(_, _, var body) => Fv(body),
            SystemFSubTerm.TypeApplication(var function, _) => Fv(function),
            _ => Set.Empty<string>()
        };
    }

    private static IEnumerable<string> FvType(SystemFSubType ty)
    {
        return ty switch
        {
            SystemFSubType.Variable(var name, _) => Set.Singleton(name),
            SystemFSubType.Union(var lhs, var rhs) => Set.Union(FvType(lhs), FvType(rhs)),
            SystemFSubType.Intersect(var lhs, var rhs) => Set.Union(FvType(lhs), FvType(rhs)),
            SystemFSubType.Arrow(var domain, var result) => Set.Union(FvType(domain), FvType(result)),
            SystemFSubType.Forall(var binder, var bound, var body) => Set.Union(FvType(bound), FvType(body).Where(i => i != binder)),
            _ => Set.Empty<string>()
        };
    }

    private static SystemFSubTerm Substitute(SystemFSubTerm term, string name, SystemFSubTerm replacement)
    {
        return term switch
        {
            SystemFSubTerm.Variable(var n) => n == name ? replacement : term,
            SystemFSubTerm.Abstraction(var binder, var binderType, var body) => Function.Block(() =>
            {
                if (binder == name) return term;
                // Performs capture-avoiding substitution, the capture of free variable can be observed in the following example:
                // if we want to substitute `lambda a. f a` with `a b`, we need to perform an alpha-conversion on the former
                // type, because if we don't, the free variable (boundless) `a` in the `a b` will be captured by the binder of
                // `lambda` and thus become bounded, which is not what we want.
                if (Fv(replacement).Contains(binder))
                {
                    // alpha-conversion: rename the binder, replace all the occurrences of the old binder with the new one in the body
                    var newBinder = UniqueStringGenerator(Set.Union(Fv(replacement), Fv(body)));
                    var newBody = Substitute(body, binder, new SystemFSubTerm.Variable(newBinder));
                    return new SystemFSubTerm.Abstraction(newBinder, binderType, Substitute(newBody, name, replacement));
                }
                return new SystemFSubTerm.Abstraction(binder, binderType, Substitute(body, name, replacement));
            }),
            SystemFSubTerm.Application(var function, var argument) =>
                new SystemFSubTerm.Application(Substitute(function, name, replacement), Substitute(argument, name, replacement)),
            SystemFSubTerm.TypeAbstraction(var binder, var bound, var body) =>
                new SystemFSubTerm.TypeAbstraction(binder, bound, Substitute(body, name, replacement)),
            SystemFSubTerm.TypeApplication(var function, var argument) =>
                new SystemFSubTerm.TypeApplication(Substitute(function, name, replacement), argument),
            SystemFSubTerm.Conditional(var condition, var then, var @else) =>
                new SystemFSubTerm.Conditional(Substitute(condition, name, replacement), Substitute(then, name, replacement), Substitute(@else, name, replacement)),
            SystemFSubTerm.IsZero(var argument) => new SystemFSubTerm.IsZero(Substitute(argument, name, replacement)),
            SystemFSubTerm.Predecessor(var argument) => new SystemFSubTerm.Predecessor(Substitute(argument, name, replacement)),
            SystemFSubTerm.Successor(var argument) => new SystemFSubTerm.Successor(Substitute(argument, name, replacement)),
            SystemFSubTerm.Fix(var argument) => new SystemFSubTerm.Fix(Substitute(argument, name, replacement)),
            _ => term
        };
    }

    private static SystemFSubType SubstituteType(SystemFSubType ty, string name, SystemFSubType replacement)
    {
        return ty switch
        {
            SystemFSubType.Variable(var n, _) => n == name ? replacement : ty,
            SystemFSubType.Union(var lhs, var rhs) =>
                new SystemFSubType.Union(SubstituteType(lhs, name, replacement), SubstituteType(rhs, name, replacement)),
            SystemFSubType.Intersect(var lhs, var rhs) =>
                new SystemFSubType.Intersect(SubstituteType(lhs, name, replacement), SubstituteType(rhs, name, replacement)),
            SystemFSubType.Arrow(var domain, var result) =>
                new SystemFSubType.Arrow(SubstituteType(domain, name, replacement), SubstituteType(result, name, replacement)),
            SystemFSubType.Forall(var binder, var bound, var body) => Function.Block(() =>
            {
                if (name == binder) return ty;
                // Performs capture-avoiding substitution, the capture of free variable can be observed in the following example:
                // if we want to substitute `forall A. A -> B` with `C -> A`, we need to perform an alpha-conversion on the former
                // type, because if we don't, the free variable (boundless) `A` in the `C -> A` will be captured by the binder of
                // `forall` and thus become bounded, which is not what we want.
                if (FvType(replacement).Contains(binder))
                {
                    var newBinder = UniqueStringGenerator(Set.Union(FvType(replacement), FvType(body)));
                    var newBody = SubstituteType(body, binder, new SystemFSubType.Variable(newBinder, true));
                    // the bound needs not to be substituted because the only scenario that the substitution will affect the bound is when
                    // the bound contains the binder, in which case it is of form like `forall X<:List<X>. X`, and that is considered illegal
                    // because System F-sub does not support recursive types. The recursive types are left for a special type system, namely
                    // F-Bounded Quantification, which combines System F, Subtyping, and Recursive Types, surprisingly, that type system is
                    // basically what languages like Java/C# use. If we don't consider the type inference (especially on generics, since the
                    // type inference of full System F is undecidable).
                    return new SystemFSubType.Forall(newBinder, bound, SubstituteType(newBody, name, replacement));
                }
                return new SystemFSubType.Forall(binder, bound, SubstituteType(body, name, replacement));
            }),
            _ => ty
        };
    }

    private static SystemFSubContextBinding? FindBinding(SystemFSubContext context, string name)
    {
        return context.FirstOrDefault(binding => binding switch
        {
            SystemFSubContextBinding.VTermBinding(var n, _) => n == name,
            SystemFSubContextBinding.VTypeBinding(var n, _) => n == name,
            _ => throw new ArgumentOutOfRangeException(nameof(binding))
        });
    }

    public static bool Subtype(SystemFSubContext context, SystemFSubType lhs, SystemFSubType rhs)
    {
        return (lhs, rhs) switch
        {
            (_, _) when lhs == rhs => true,
            (_, SystemFSubType.Top) => true,
            (_, SystemFSubType.Bottom) => false,
            (SystemFSubType.Variable(var lhsName, _), _) => FindBinding(context, lhsName) switch
            {
                SystemFSubContextBinding.VTypeBinding(_, var bound) => Subtype(context, bound, rhs),
                _ => false
            },
            (SystemFSubType.Arrow(var lhsDomain, var lhsResult), SystemFSubType.Arrow(var rhsDomain, var rhsResult)) =>
                Subtype(context, rhsDomain, lhsDomain) && Subtype(context, lhsResult, rhsResult),
            (SystemFSubType.Forall(var lhsBinder, var lhsBound, var lhsBody), SystemFSubType.Forall(var rhsBinder, var rhsBound, var rhsBody)) => Function.Block(() =>
            {
                // binder is contravariant
                var binderCompliant = Subtype(context, rhsBound, lhsBody);
                var newBinderName = UniqueStringGenerator(Set.BigUnion(FvType(lhsBody), FvType(rhsBody),
                    from binding in context.OfType<SystemFSubContextBinding.VTypeBinding>() select binding.Name));
                // unify the binder of two types for comparison
                var newLhsBody = SubstituteType(lhsBody, lhsBinder, new SystemFSubType.Variable(newBinderName, true));
                var newRhsBody = SubstituteType(rhsBody, rhsBinder, new SystemFSubType.Variable(newBinderName, true));
                var newContext = WidenContext(context, new SystemFSubContextBinding.VTypeBinding(newBinderName, rhsBound));
                return binderCompliant && Subtype(newContext, newLhsBody, newRhsBody);
            }),
            (_, SystemFSubType.Union(var lhsUnion, var rhsUnion)) => Subtype(context, lhs, lhsUnion) || Subtype(context, lhs, rhsUnion),
            (_, SystemFSubType.Intersect(var lhsIntersect, var rhsIntersect)) => Subtype(context, lhs, lhsIntersect) && Subtype(context, lhs, rhsIntersect),
            _ => false
        };
    }

    private static SystemFSubType? TryPromote(SystemFSubContext context, SystemFSubType input)
    {
        static SystemFSubType? FindFirstNonMonoType(SystemFSubContext context, SystemFSubType input)
        {
            if (input is SystemFSubType.Variable(var name, true))
            {
                var bound = context.OfType<SystemFSubContextBinding.VTypeBinding>()
                    .FirstOrDefault(b => b is var (n, _) && n == name)?.Bound;
                return bound switch
                {
                    null => null,
                    SystemFSubType.Variable(_, true) => FindFirstNonMonoType(context, bound),
                    _ => bound
                };
            }

            return input;
        }

        return FindFirstNonMonoType(context, input);
    }
    
    public static SystemFSubType TypeOf(SystemFSubContext context, SystemFSubTerm term)
    {
        SystemFSubType CheckNat(SystemFSubTerm argument)
        {
            return TypeOf(context, argument) is var argumentType && argumentType == SystemFSubType.NatType
                ? SystemFSubType.BoolType
                : throw new TypeMismatchException($"Type mismatch: expected nat, got {argumentType}");
        }

        return term switch
        {
            SystemFSubTerm.Variable(var name) => FindBinding(context, name) switch
            {
                SystemFSubContextBinding.VTermBinding(_, var termType) => termType,
                _ => throw new TypeMismatchException($"Type mismatchCannot find variable of name {name} in context")
            },
            SystemFSubTerm.Abstraction(var binder, var binderType, var body) =>
                new SystemFSubType.Arrow(binderType,
                    TypeOf(WidenContext(context, new SystemFSubContextBinding.VTermBinding(binder, binderType)), body)),
            SystemFSubTerm.Application(var function, var argument) => Function.Block(() =>
            {
                var fType = TypeOf(context, function);
                var argumentType = TypeOf(context, argument);
                return TryPromote(context, fType) is SystemFSubType.Arrow(var domain, var result)
                    ? Subtype(context, argumentType, domain)
                        ? result
                        : throw new TypeMismatchException($"Type mismatch: expected argument type to be a subtype of {domain}, got {argumentType}")
                    : throw new TypeMismatchException($"Type mismatch: expected arrow type, got {fType}");
            }),
            SystemFSubTerm.TypeAbstraction(var binder, var bound, var body) =>
                new SystemFSubType.Forall(binder, bound, TypeOf(WidenContext(context, new SystemFSubContextBinding.VTypeBinding(binder, bound)), body)),
            SystemFSubTerm.TypeApplication(var abstraction, var argumentType) => TryPromote(context, TypeOf(context, abstraction)) switch
            {
                SystemFSubType.Forall(var binder, var bound, var body) =>
                    Subtype(context, argumentType, bound)
                        ? SubstituteType(body, binder, argumentType)
                        : throw new TypeMismatchException($"Type mismatch: expected argument type to be a subtype of {bound}, got {argumentType}"),
                var ty => throw new TypeMismatchException($"Type mismatch: expected generic (forall) type, got {ty}")
            },
            SystemFSubTerm.Conditional(var condition, var thenBranch, var elseBranch) => Function.Block(() =>
            {
                var conditionType = TypeOf(context, condition);
                var thenBranchType = TypeOf(context, thenBranch);
                var elseBranchType = TypeOf(context, elseBranch);
                return conditionType is SystemFSubType.BoolPrimitive
                    ? new SystemFSubType.Union(thenBranchType, elseBranchType)
                    : throw new TypeMismatchException($"Type mismatch: expected boolean condition, got {conditionType}");
            }),
            SystemFSubTerm.BoolLiteral => SystemFSubType.BoolType,
            SystemFSubTerm.NatLiteral => SystemFSubType.NatType,
            SystemFSubTerm.IsZero(var argument) => CheckNat(argument),
            SystemFSubTerm.Successor(var argument) => CheckNat(argument),
            SystemFSubTerm.Predecessor(var argument) => CheckNat(argument),
            SystemFSubTerm.Fix(var argument) =>
                TypeOf(context, argument) is SystemFSubType.Arrow(SystemFSubType.Arrow fixpoint, SystemFSubType.Arrow body) && fixpoint == body
                    ? fixpoint
                    : throw new TypeMismatchException($"Type mismatch: the type of a fix operator must be a function type, which, accepts a function type, and returns an identical function type"),
            _ => throw new ArgumentOutOfRangeException(nameof(term), term, null)
        };
    }
}
