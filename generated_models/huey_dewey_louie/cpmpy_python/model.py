# huey_dewey_louie: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install cpmpy`) with:
#   python huey_dewey_louie.py

import cpmpy as cp


def create_model(instance):
    """Huey, Dewey and Louie are cub scouts questioned by their uncle, so they cannot
    lie and each of their statements is true. Who is guilty?"""
    # The puzzle states the three statements itself, so the instance is not used.

    # guilty[0], guilty[1], guilty[2]: whether Huey, Dewey, Louie is guilty
    guilty = cp.boolvar(shape=3, name="guilty")
    huey, dewey, louie = guilty

    model = cp.Model()
    # Huey: Dewey and Louie have an equal share; if one is guilty, so is the other.
    model.add(dewey == louie)
    # Dewey: if Huey is guilty, then so is Dewey.
    model.add(huey.implies(dewey))
    # Louie: Dewey and Louie are not both guilty.
    model.add(~(dewey & louie))

    return model, {"huey": huey, "dewey": dewey, "louie": louie}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
