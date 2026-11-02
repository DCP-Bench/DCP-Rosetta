# zebra: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python zebra.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def create_model(instance):
    """Five houses stand in a row, numbered 0 (left) to 4 (right). Each house has
    a different color, inhabitant nationality, pet, drink and job. From the clues,
    find the house of every color, nationality, pet, drink and job."""
    n_houses = 5  # the houses in the row

    # The values of each attribute, one for each house.
    attributes = {
        "colors": ["yellow", "green", "red", "white", "blue"],
        "nations": ["italy", "spain", "japan", "england", "norway"],
        "pets": ["cat", "zebra", "bear", "snails", "horse"],
        "drinks": ["milk", "water", "tea", "coffee", "juice"],
        "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
    }

    # in_house[a][v][h] is true when value v of attribute a is in house h
    in_house = {
        a: {v: [Bool(f"{a}_{v}_in_house_{h}") for h in range(n_houses)] for v in values}
        for a, values in attributes.items()
    }
    # position[a][v] is the house number of value v of attribute a
    position = {
        a: {v: sum(h * in_house[a][v][h] for h in range(n_houses)) for v in values}
        for a, values in attributes.items()
    }

    constraints = []

    # Each value of an attribute is in exactly one house.
    for a, values in attributes.items():
        for v in values:
            constraints.append(sum(in_house[a][v]) == 1)

    # Each house holds exactly one value of each attribute.
    for a, values in attributes.items():
        for h in range(n_houses):
            constraints.append(sum(in_house[a][v][h] for v in values) == 1)

    # The painter owns the horse.
    constraints.append(position["jobs"]["painter"] == position["pets"]["horse"])
    # The diplomat drinks coffee.
    constraints.append(position["jobs"]["diplomat"] == position["drinks"]["coffee"])
    # The one who drinks milk lives in the white house.
    constraints.append(position["drinks"]["milk"] == position["colors"]["white"])
    # The Spaniard is a painter.
    constraints.append(position["nations"]["spain"] == position["jobs"]["painter"])
    # The Englishman lives in the red house.
    constraints.append(position["nations"]["england"] == position["colors"]["red"])
    # The snails are owned by the sculptor.
    constraints.append(position["pets"]["snails"] == position["jobs"]["sculptor"])
    # The green house is immediately on the left of the red one.
    constraints.append(position["colors"]["green"] + 1 == position["colors"]["red"])
    # The Norwegian lives immediately on the right of the blue house.
    constraints.append(position["nations"]["norway"] == position["colors"]["blue"] + 1)
    # The doctor drinks milk.
    constraints.append(position["jobs"]["doctor"] == position["drinks"]["milk"])
    # The diplomat is Japanese.
    constraints.append(position["jobs"]["diplomat"] == position["nations"]["japan"])
    # The Norwegian owns the zebra.
    constraints.append(position["nations"]["norway"] == position["pets"]["zebra"])
    # The green house is next to the white one, on either side.
    constraints.append(Or([position["colors"]["green"] + 1 == position["colors"]["white"],
                           position["colors"]["white"] + 1 == position["colors"]["green"]]))
    # The horse is owned by a neighbor of the diplomat, on either side.
    constraints.append(Or([position["pets"]["horse"] + 1 == position["jobs"]["diplomat"],
                           position["jobs"]["diplomat"] + 1 == position["pets"]["horse"]]))
    # The Italian lives in the red, white or green house.
    constraints.append(Or([position["nations"]["italy"] == position["colors"]["red"],
                           position["nations"]["italy"] == position["colors"]["white"],
                           position["nations"]["italy"] == position["colors"]["green"]]))

    # the house number of each color, nationality, pet, drink and job
    outputs = {a: [position[a][v] for v in values] for a, values in attributes.items()}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
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
