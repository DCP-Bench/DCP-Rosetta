# IDP-Z3 (FO(.)) — FO(.), first-order model expansion over finite domains (Z3-backed)

## Minimal working example (knapsack)
```idp
vocabulary V {
    type I <: Int
    values, weights: I -> Int
    capacity: () -> Int
    x: I -> Bool
    maximize: () -> Int
}
theory T:V {
    sum{{ weights(i) | i in I: x(i) }} =< capacity().
    maximize() = sum{{ values(i) | i in I: x(i) }}.
}
structure S:V {
    I := {0..2}. values := {0 -> 6, 1 -> 10, 2 -> 12}. weights := {0 -> 1, 1 -> 2, 2 -> 3}. capacity := 5.
}
procedure main() {
    print(maximize(T, S, term="maximize()"))
}
```

## API
- **Decision variables:** in `vocabulary`: `type I <: Int`; `c: () -> Int`; `f: I -> Int`; `g: I * J -> Int`; `p: I -> Bool`; `partial f: I -> Int` (guard every use); integer-valued symbols need bounds in the theory; every declared type needs an interpretation (e.g. `T := {0..4}.` in a structure)
- **Logic constraints:** `&`, `|`, `~`, `=>`, `<=>`; `!i in I: phi.`; `!i, j in I: phi.`; `?i in I: phi.`; `if c then a else b`
- **Arithmetic constraints:** `=`, `~=`, `<`, `=<`, `>`, `>=`; `+ - * / %`; `abs(e)`; `sum{{ t | i in I: phi }}` (a product term needs parentheses: `sum{{ (w(i) * f(i)) | i in I: p(i) }}`)
- **Other constraints:**
  - counting: `#{ i in I: phi }`
  - indexing/extensional: `f(e)` with a variable index; tables as interpretations in `structure`: `r := {(0, 2), (1, 0)}.`, `f := {0 -> 6, 1 -> 10}.`
- **Objectives and solving:** `maximize: () -> Int` (any name) with `maximize() = e.` in the theory; `print(maximize(T, S, term="maximize()"))` or `minimize(...)` in `procedure main()`; satisfaction: `model_check(T, S)` (sat/unsat), `model_expand(T, S, max=1)` (generator of models)

## Modelling
- **Domains:** bound every integer symbol as tightly as the data allows
- **Grounding:** every quantifier is grounded over its types: avoid quantifiers over 4 variables; say what must exist instead, e.g. `!i in I: x(i) < m() => ?j in I: x(j) = x(i) + 1 & adj(i, j).`; write fixed offsets as equalities (`r2 = r1 + 2 | r1 = r2 + 2`), not `abs`
- **Products:** a product of two symbols where one has a small domain: split on its values, `!t in T, k in K: l(t) = k => c(t) = k * p(t).`
- **Symmetry:** order interchangeable values, `!i, j in I: j = i + 1 => a(i) < a(j).`, instead of pairwise `~=`, and fix the first
- **Implied constraints:** add totals the solver cannot infer (Σ capacity ≥ Σ demand, count bounds on prefixes of a sequence)

Docs: https://docs.idp-z3.be/
