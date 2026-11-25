---
name: dcp-groundfox
description: GroundFOX, the proof-logging grounder of the CertiFOX toolkit (KU Leuven), which turns a finite-domain first-order model expansion problem (a .fox file - vocabulary, theory in grounding normal form, structure) into DIMACS CNF for any SAT solver; checkfox verifies its proof log. Use when writing, debugging or running FOX models with groundfox, or solving a satisfaction problem by grounding first-order logic to SAT.
license: MPL-2.0
compatibility: Built from source (C++23 compiler, CMake 3.25+, Java 11+ for ANTLR, git); tested with GroundFOX 0.1.2 (commit f30fb9c). Needs a separate SAT solver; the examples use python-sat (pip install python-sat). No licence key.
metadata:
  domain: constraint-programming
  solver: groundfox
  paradigm: sat
  interfaces: "fox"
---

# GroundFOX (FOX) — first-order model expansion, grounded to SAT

A `.fox` file has an `invocabulary` (data, interpreted by the `structure`), an
`outvocabulary` (unknowns), a `theory` and a `structure`. `groundfox` grounds it to CNF and a
symbol table; a SAT solver finds a model. There is **no arithmetic, no aggregate and no
objective**: numbers are plain domain elements, so every numeric relation is data you
compute in the structure. Install, CLI, proofs:
[interfaces/fox.md](interfaces/fox.md).

## Minimal working example (graph colouring)
```python
import subprocess
from pysat.solvers import Solver
nodes, colours, edges = [0, 1, 2, 3], ["red", "green", "blue"], [(0, 1), (1, 2), (2, 0), (2, 3)]
fox = """invocabulary { Node/1 Colour/1 Edge/2 }
outvocabulary { colour/2 }
theory {
    ! n [Node(n)] : ? c [Colour(c)] : colour(n, c).
    ! n [Node(n)] : ! c [Colour(c)] : ! d [Colour(d) & c ~= d] : ~colour(n, c) | ~colour(n, d).
    ! a : ! b [Edge(a, b)] : ! c [Colour(c)] : ~colour(a, c) | ~colour(b, c).
}
structure {
    domain = { %s }
    Node = { %s }
    Colour = { %s }
    Edge = { %s }
}
""" % (" ; ".join(map(str, nodes + colours)), " ; ".join(map(str, nodes)), " ; ".join(colours),
       " ; ".join(f"({a},{b})" for a, b in edges))
open("colouring.fox", "w").write(fox)
subprocess.run(["groundfox", "-i", "colouring.fox", "-o", "colouring.cnf", "-t", "colouring.sym", "--no-proof"],
               check=True, capture_output=True)
clauses = [[int(x) for x in line.split()[:-1]] for line in open("colouring.cnf") if line[0] not in "cp"]
atoms = {int(v): a for _, v, a in (line.split(None, 2) for line in open("colouring.sym"))}
with Solver(name="glucose42", bootstrap_with=clauses) as solver:
    if solver.solve():
        print(sorted(atoms[v].strip() for v in solver.get_model() if v > 0 and v in atoms))
    else:
        print("unsatisfiable")
```

## Language
- **Vocabulary:** `invocabulary { Node/1 Edge/2 Big/0 }`, `outvocabulary { colour/2 }`: arity always (`Big/0` for a proposition), no `;` between declarations
- **Structure:** `domain = { a ; b ; 0 ; 7 }`; `Node = { a ; b }`; `Edge = { (a,b) ; (b,a) }`; `Empty = {}`; `Big = true`. Elements are identifiers (start with a letter) or non-negative integers; every constant used in the theory must be in the domain
- **Sentences:** end with `.`; `! x [guard] : body` (∀), `? x [guard] : body` (∃), **one variable per quantifier** (`! x : ! y [...]`); the body runs to the end of the sentence
- **Guards:** input symbols only, with `&`, `|`, `~`, `=`, `~=` and unguarded quantifiers (`[Node(x) & ~? y : Edge(x, y)]`)
- **Bodies (GNF):** under the `!`s, a `&` of clauses; a clause is `|` of literals (`colour(n, c)`, `~colour(n, c)`, `x ~= y`, constants like `colour(0, red)`), or one `? y [guard] :` holding it all. For a valid proof, every sentence has a quantifier (`! u [u = 0] : x(0).`) and no `?` sits beside literals or in another `?`
- **Rejected** ("not in Grounding Normal Form"): `=>`, `<=>`, `~( ... )` around a non-atom, `&` under `?`; an output symbol in a guard
- **Running:** `groundfox -i m.fox -o m.cnf -t m.sym --no-proof`; `m.sym` maps variables to atoms; an atom no sentence mentions is not in the CNF; a `?` over an empty guard is false

## Modelling
- **Domains:** one unary input symbol per sort (`Row/1`, `Val/1`), a guard on every quantified variable, and per-variable value sets cut from the data; the theory is fixed text, so sizes and bounds come in as relations
- **Structure:** a function `x: I -> V` is `x(i, v)` with at least one `! i [I(i)] : ? v [V(v)] : x(i, v).` and at most one `! i [I(i)] : ! v [V(v)] : ! w [V(w) & v ~= w] : ~x(i, v) | ~x(i, w).`; over many values use a ladder instead: `~x(i, v) | seen(i, v)`, and for `Next(v, w)` `~seen(i, v) | seen(i, w)` and `~seen(i, v) | ~x(i, w)`. All-different: `~x(i, v) | ~x(j, v)` for `i ~= j`
- **Lookups:** compute every numeric or geometric relation in the structure (`Attack(r1, c1, r2, c2)`, `Less/2`, `Next/2`, allowed tuples) and forbid each bad combination: `! a : ! b [Clash(a, b)] : ~x(0, a) | ~x(1, b).`
- **Sums, counts, patterns:** layered states `S(k, s)` forced forward by a data table: `~S(i, s) | ~pick(i, 1) | S(j, t)` for `Next(i, j)`, `W(i, w)`, `Add(s, w, t)`; a pattern is an automaton `Q(k, q)` with transitions `Delta(q, a, r)` computed in the structure. Every (state, step) pair needs a successor or an explicit ban (an absorbing overflow or dead state), else the chain escapes; then forbid the wrong final states (`! l [Last(l)] : ! s [Val(s) & ~Target(s)] : ~S(l, s).`)
- **Implied constraints:** at least one state per layer, and every true state has a true predecessor: chains get much easier
- **Size:** each sentence grounds the product of its variables' guards; keep it near 10^5 clauses, never enumerate subsets

Docs: <https://gitlab.kuleuven.be/krr/software/groundfox-checkfox> (README, `docs/FOX_EBNF.md`), <https://gitlab.kuleuven.be/krr/software/certifox/-/blob/main/inputSyntax.md>
