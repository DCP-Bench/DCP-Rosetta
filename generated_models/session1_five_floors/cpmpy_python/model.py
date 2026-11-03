# session1_five_floors: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install cpmpy`) with:
#   python session1_five_floors.py

import cpmpy as cp


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors of a
    five-floor apartment house; find their floors from the stated clues."""
    # The puzzle has no instance data: the clues are the problem statement.

    # The floor (1 to 5) where each person lives
    baker, cooper, fletcher, miller, smith = cp.intvar(
        1, 5, shape=5, name=["B", "C", "F", "M", "S"]
    )

    model = cp.Model()

    # They all live on different floors.
    model.add(cp.AllDifferent([baker, cooper, fletcher, miller, smith]))

    # Baker does not live on the fifth floor.
    model.add(baker != 5)

    # Cooper does not live on the first floor.
    model.add(cooper != 1)

    # Fletcher lives on neither the fifth nor the first floor.
    model.add((fletcher != 5) & (fletcher != 1))

    # Miller lives on a higher floor than Cooper.
    model.add(miller > cooper)

    # Smith does not live on a floor adjacent to Fletcher's.
    model.add(cp.abs(smith - fletcher) != 1)

    # Fletcher does not live on a floor adjacent to Cooper's.
    model.add(cp.abs(fletcher - cooper) != 1)

    return model, {"B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
