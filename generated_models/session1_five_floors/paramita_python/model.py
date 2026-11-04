# session1_five_floors: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session1_five_floors.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf

# The floors, numbered from the first to the fifth
FLOORS = range(1, 6)
# The five people, by initial
PEOPLE = ["B", "C", "F", "M", "S"]


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on the first five floors of
    an apartment house, one person to a floor; find the floor of each person."""
    # The floors each person may live on, after the clues that rule some out
    floors = {
        "B": [1, 2, 3, 4],  # Baker does not live on the fifth floor
        "C": [2, 3, 4, 5],  # Cooper does not live on the first floor
        "F": [2, 3, 4],     # Fletcher lives on neither the fifth nor the first floor
        "M": FLOORS,
        "S": FLOORS,
    }

    # on_floor[p][v] is true when person p lives on floor v
    on_floor = {p: {v: Bool(f"floor_{p}_{v}") for v in floors[p]} for p in PEOPLE}

    # The floor each person lives on
    floor = {p: sum(v * on_floor[p][v] for v in on_floor[p]) for p in PEOPLE}

    # Persons p and q do not live on adjacent floors.
    def not_next_to(p, q):
        return [~(on_floor[p][v] & on_floor[q][w])
                for v in FLOORS for w in (v - 1, v + 1)
                if v in on_floor[p] and w in on_floor[q]]

    # The rules the floors must satisfy.
    subject_to = []

    # Each person lives on exactly one floor.
    for p in PEOPLE:
        subject_to.append(sum(on_floor[p].values()) == 1)

    # The five people live on different floors, so each floor holds one person.
    for v in FLOORS:
        subject_to.append(sum(on_floor[p][v] for p in PEOPLE if v in on_floor[p]) == 1)

    # Miller lives on a higher floor than Cooper.
    subject_to.append(floor["M"] >= floor["C"] + 1)

    # Smith does not live on a floor adjacent to Fletcher's.
    subject_to += not_next_to("S", "F")

    # Fletcher does not live on a floor adjacent to Cooper's.
    subject_to += not_next_to("F", "C")

    outputs = {p: floor[p] for p in PEOPLE}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

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
