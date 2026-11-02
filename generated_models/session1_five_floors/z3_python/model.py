# session1_five_floors: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install z3-solver numpy`) with:
#   python session1_five_floors.py

import z3


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors of a
    five-floor apartment house; find their floors from the stated clues."""
    # The puzzle has no instance data: the clues are the problem statement.

    # The floor (1 to 5) where each person lives
    baker, cooper, fletcher, miller, smith = people = [z3.Int(name) for name in "BCFMS"]

    solver = z3.Solver()

    # Each floor is from 1 to 5.
    solver.add([z3.And(1 <= floor, floor <= 5) for floor in people])

    # They all live on different floors.
    solver.add(z3.Distinct(people))

    # Baker does not live on the fifth floor.
    solver.add(baker != 5)

    # Cooper does not live on the first floor.
    solver.add(cooper != 1)

    # Fletcher lives on neither the fifth nor the first floor.
    solver.add(z3.And(fletcher != 5, fletcher != 1))

    # Miller lives on a higher floor than Cooper.
    solver.add(miller > cooper)

    # Smith does not live on a floor adjacent to Fletcher's.
    solver.add(z3.Abs(smith - fletcher) != 1)

    # Fletcher does not live on a floor adjacent to Cooper's.
    solver.add(z3.Abs(fletcher - cooper) != 1)

    return solver, {"B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
