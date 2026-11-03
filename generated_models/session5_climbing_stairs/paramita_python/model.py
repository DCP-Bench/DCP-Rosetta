# session5_climbing_stairs: a Paramita (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move.
    Find the number of steps taken at each move, or 0 once the top is reached."""
    n_steps = instance["n"]  # the number of steps in the stair
    m1 = instance["m1"]      # the fewest steps taken at a move
    m2 = instance["m2"]      # the most steps taken at a move

    # values: the amounts a move can take, from m1 to m2
    values = list(range(m1, m2 + 1))

    # takes[i][v] is true when move i takes v steps; v = 0 means no steps, once the top is reached
    takes = [{v: Bool(f"move_{i}_takes_{v}") for v in [0] + values} for i in range(n_steps)]

    # steps[i]: the number of steps taken at move i
    steps = [sum(v * takes[i][v] for v in values) for i in range(n_steps)]

    # the conditions every climb must meet
    constraints = []
    # Each move takes exactly one of the amounts, 0 included.
    constraints += [sum(takes[i].values()) == 1 for i in range(n_steps)]
    # Once a move takes no steps, every later move takes no steps.
    constraints += [If(takes[i][0], takes[i + 1][0]) for i in range(n_steps - 1)]
    # The moves together climb the whole stair.
    constraints.append(sum(steps) == n_steps)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"steps": steps}


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
