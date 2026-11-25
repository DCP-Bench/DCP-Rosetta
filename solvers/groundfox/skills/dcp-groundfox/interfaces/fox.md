# GroundFOX with `.fox` files (command line)

## Install

GroundFOX ships as C++ source ([repository](https://gitlab.kuleuven.be/krr/software/groundfox-checkfox),
README *Building from Source*). It needs a C++23 compiler (GCC 14 works), CMake 3.25+, Java 11+ (ANTLR
generates the parser at build time) and git; CMake fetches ANTLR and doctest.

```sh
git clone https://gitlab.kuleuven.be/krr/software/groundfox-checkfox.git && cd groundfox-checkfox
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
cmake --build build --parallel 8          # build/groundfox/groundfox, build/checkfox/checkfox
cmake --install build --prefix ~/.local   # optional
pip install python-sat                    # a SAT solver for the CNF
```

GCC 11 and CMake 3.22 (Ubuntu 22.04) are too old; use a newer distribution or toolchain.

## Command line

| Task | Command |
| --- | --- |
| Ground to DIMACS + symbol table | `groundfox -i m.fox -o m.cnf -t m.sym --no-proof` |
| Ground with a proof log | `groundfox -i m.fox -o m.cnf -p m.cfx -t m.sym` |
| Check the proof | `checkfox -i m.fox -o m.cnf -p m.cfx` (exit 0 accepted, 1 rejected, 2 unreadable) |
| Leave the certified fragment | `--nested-guards`, `--functions`, `--arbitrary-fol` (same flags for checkfox; may crash) |
| Sizes and timings | `-S` |

Without `-t` the symbol table goes to `<input>_symbols.txt`; without `-o` the output is
`<input>_out.fox`. Statistics go to stdout and errors to stderr with exit code 1.

## Reading a solution

`m.sym` has one line `PRED <var> name(arg1,arg2)` per atom in the CNF. Map the positive
literals of the SAT model through it and keep the output symbols you want. An out atom that
no sentence mentions is not in the CNF: it is unconstrained, so read it as false only when
your theory mentions every atom you report.

## All solutions

Load the CNF into an incremental solver and, after each model, add a clause that negates the
current values of the atoms you report (not of auxiliary atoms, or one answer comes back
many times). Unsatisfiable means no further solution.

```python
report = [v for v, atom in atoms.items() if atom.startswith("colour(")]
while solver.solve():
    model = set(l for l in solver.get_model() if l > 0)
    print(sorted(atoms[v].strip() for v in report if v in model))
    solver.add_clause([-v if v in model else v for v in report])
```

## Common issues

| Symptom | Fix |
| --- | --- |
| `no viable alternative at input 'Q}'` | a proposition needs its arity: `Q/0` |
| `mismatched input ','` after `!` | one variable per quantifier: `! x : ! y [...]` |
| `formula is not in Grounding Normal Form (GNF)` | rewrite `a => b` as `~a \| b`, `<=>` as two sentences, push `~` to atoms, no `&` under `?` |
| `quantifier guard must be an input formula` | move the output literal from the guard into the body as a disjunct |
| `Number 7 is not in the domain` | add every constant of the theory to `domain` |
| `unsatisfiability detected during grounding` | a `?` with an empty guard, or a body that is false for some instance of the `!`s |
| checkfox: `Proof incomplete: N formula(s) remain` | GroundFOX 0.1.2 proofs miss two forms: a sentence with no quantifier (wrap it: `! u [u = 0] : x(0).`) and `literal \| ? y [G] : body` (move the literal into the body, `? y [G] : body \| literal`, when `G` is never empty), and `? a : ? b : ...` (split with an auxiliary predicate) |
| Grounding is slow or huge | a quantifier guarded by the whole domain; give it a unary sort or a precomputed relation |

## Runnable examples

- [colouring](../assets/fox/colouring/README.md): the graph colouring of SKILL.md.
