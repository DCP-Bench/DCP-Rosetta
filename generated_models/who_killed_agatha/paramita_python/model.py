# who_killed_agatha: a Paramita (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python who_killed_agatha.py who_killed_agatha.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents, and the clues about who hates whom and who
    is richer than whom identify the killer."""
    names = instance["names"]  # names[i]: the name of resident i
    n_residents = len(names)   # the number of residents

    # The residents named in the story.
    agatha = names.index("Agatha herself")
    butler = names.index("the butler")
    charles = names.index("Charles")

    # killer[x] is true when resident x killed Agatha
    killer = [Bool(f"killer_{x}") for x in range(n_residents)]
    # hates[x][y] is true when resident x hates resident y
    hates = [[Bool(f"hates_{x}_{y}") for y in range(n_residents)] for x in range(n_residents)]
    # richer[x][y] is true when resident x is richer than resident y
    richer = [[Bool(f"richer_{x}_{y}") for y in range(n_residents)] for x in range(n_residents)]

    constraints = []

    # Nobody is richer than himself.
    constraints += [~richer[x][x] for x in range(n_residents)]
    # Of two residents, at most one is richer than the other.
    constraints += [If(richer[x][y], ~richer[y][x]) for x in range(n_residents) for y in range(n_residents)]
    # If x is richer than y and y is richer than z, then x is richer than z.
    constraints += [If(richer[x][y] & richer[y][z], richer[x][z])
                    for x in range(n_residents) for y in range(n_residents) for z in range(n_residents)]

    # Exactly one resident killed Agatha.
    constraints.append(sum(killer) == 1)

    # A killer hates Agatha.
    constraints += [If(killer[x], hates[x][agatha]) for x in range(n_residents)]
    # A killer is no richer than Agatha.
    constraints += [If(killer[x], ~richer[x][agatha]) for x in range(n_residents)]

    # Charles hates no one that Agatha hates.
    constraints += [If(hates[agatha][y], ~hates[charles][y]) for y in range(n_residents)]

    # Agatha hates everybody except the butler.
    constraints += [~hates[agatha][y] if y == butler else hates[agatha][y] for y in range(n_residents)]

    # The butler hates everyone who is not richer than Agatha.
    constraints += [If(~richer[y][agatha], hates[butler][y]) for y in range(n_residents)]
    # The butler hates everyone whom Agatha hates.
    constraints += [If(hates[agatha][y], hates[butler][y]) for y in range(n_residents)]

    # No one hates everyone: each resident fails to hate at least one resident.
    constraints += [sum(~hates[x][y] for y in range(n_residents)) >= 1 for x in range(n_residents)]

    # the index of the resident who killed Agatha
    killer_index = sum(x * killer[x] for x in range(n_residents))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"killer": killer_index}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
