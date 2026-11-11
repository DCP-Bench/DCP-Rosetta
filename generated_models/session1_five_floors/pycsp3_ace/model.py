# session1_five_floors: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python session1_five_floors.py

from pycsp3 import *


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on the first five floors of an apartment
    house, one each. Baker is not on the fifth floor, Cooper not on the first, Fletcher neither
    on the fifth nor the first. Miller is on a higher floor than Cooper. Smith and Fletcher are
    not on adjacent floors, and neither are Fletcher and Cooper. Find the floor of each person."""
    n_floors = 5                 # the house has five floors
    first_floor = 1              # the lowest floor
    top_floor = n_floors         # the fifth floor, the highest of the house

    # The floor of each person, from the first to the fifth floor.
    baker = Var(dom=range(first_floor, top_floor + 1))    # the floor where Baker lives
    cooper = Var(dom=range(first_floor, top_floor + 1))   # the floor where Cooper lives
    fletcher = Var(dom=range(first_floor, top_floor + 1)) # the floor where Fletcher lives
    miller = Var(dom=range(first_floor, top_floor + 1))   # the floor where Miller lives
    smith = Var(dom=range(first_floor, top_floor + 1))    # the floor where Smith lives

    satisfy(
        # They all live on different floors.
        AllDifferent(baker, cooper, fletcher, miller, smith),
        # Baker does not live on the fifth floor.
        baker != top_floor,
        # Cooper does not live on the first floor.
        cooper != first_floor,
        # Fletcher does not live on either the fifth or the first floor.
        fletcher != top_floor,
        fletcher != first_floor,
        # Miller lives on a higher floor than Cooper.
        miller > cooper,
        # Smith does not live on a floor adjacent to Fletcher's.
        abs(smith - fletcher) != 1,
        # Fletcher does not live on a floor adjacent to Cooper's.
        abs(fletcher - cooper) != 1,
    )

    return {"B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
