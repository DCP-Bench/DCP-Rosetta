# clingo (ASP) — ASP in clingo syntax, grounding plus CDCL answer-set solving

## Minimal working example (knapsack)
```
value(0,6). value(1,10). value(2,12). weight(0,1). weight(1,2). weight(2,3). capacity(5).
{ take(I) : value(I,_) }.
:- #sum { W,I : take(I), weight(I,W) } > C, capacity(C).
#maximize { V,I : take(I), value(I,V) }.
#show take/1.
```
Optimum 22 (clingo reports cost -22 for `#maximize`), answer `take(1) take(2)`.

## API
- **Decision variables:** a choice rule over a domain predicate: `{ take(I) : item(I) }.` (any subset); `1 { x(I,V) : val(V) } 1 :- item(I).` (exactly one value per `I`); bounds `L { ... } U`; `V = 0..9` and `(a;b)` pools give domains; `#const n=4.`
- **Logic constraints:** integrity constraint `:- body.` forbids the body; rules `h :- a, not b.` (default negation `not`; every variable must occur in a positive body literal); `h :- a ; b.` conjunction
- **Arithmetic constraints:** comparisons `=`, `!=`, `<`, `<=`, `>`, `>=` between terms; `+ - * / \ **` and `|X|` (integer division, `\` is modulo); ranges `I = 0..n-1`
- **Other constraints:**
  - counting: `#count { I : x(I,V) }` as a term (`N = #count { ... }`) or as a bound `:- #count { I : z(I) } > 3.`, `:- 1 #count { ... } 1.`
  - sums: `#sum { C,I : y(I), cost(I,C) }` (elements are tuples `weight,key`; the key keeps equal weights as separate terms); `#max { V : p(V) }`, `#min { V : p(V) }`
  - indexing/extensional: facts are tables; join them in a body `:- x(I,V), cost(I,C), ...`; `_` is the anonymous variable
- **Objectives and solving:** `#minimize { C,I : y(I), cost(I,C) }.` / `#maximize { ... }.` (tuple elements as in `#sum`); `#show p/2.` selects printed predicates, `#show t(I) : y(I).` prints derived terms; `#project p/1.`

## Modelling
- **Domains:** keep the domain predicates tight (`val(1..3)`) and range over them in every choice rule; an unbounded or loosely bounded `V = 0..1000` multiplies the grounding
- **Structure:** exactly-one and permutations are two-sided choice rules, `1 { p(K,O) : op(O) } 1 :- pos(K).  1 { p(K,O) : pos(K) } 1 :- op(O).`; capacities and totals are one `#sum`/`#count` constraint over the choices, not pairwise rules
- **Lookups:** keep data as facts and join them in the rule body; derive helper predicates once (`score(S) :- S = #sum { H*V,I : hits(I,H), tgt(I,V) }.`) and reuse them
- **Symmetry:** break interchangeable choices with an ordering constraint, `:- x(I,V), x(J,W), I<J, V>W.`
- **Implied constraints:** add redundant `#count`/`#sum` bounds that the grounder cannot infer, e.g. a total over all items next to the per-group ones
- **Grounding size:** keep rule bodies short (few free variables); split a long join into intermediate predicates; avoid large `**` or product terms over wide domains

Docs: https://potassco.org/clingo/
