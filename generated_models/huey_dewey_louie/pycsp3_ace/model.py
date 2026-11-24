# huey_dewey_louie: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python huey_dewey_louie.py

from pycsp3 import *


def create_model(instance):
    """Huey, Dewey and Louie are questioned by their uncle about who is guilty. Huey says
    that Dewey and Louie have an equal share in it, and that if one is guilty so is the
    other. Dewey says that if Huey is guilty then so is he. Louie says that he and Dewey
    are not both guilty. They are cub scouts and cannot tell a lie, so every statement is
    true. Find whether each of them is guilty."""
    # Each variable is 1 when that person is guilty and 0 when not.
    huey = Var(dom={0, 1})  # Huey is guilty
    dewey = Var(dom={0, 1})  # Dewey is guilty
    louie = Var(dom={0, 1})  # Louie is guilty

    satisfy(
        # Huey's statement is true: Dewey and Louie are both guilty or both innocent.
        dewey == louie,
        # Dewey's statement is true: if Huey is guilty, then Dewey is guilty.
        imply(huey, dewey),
        # Louie's statement is true: Dewey and Louie are not both guilty.
        dewey + louie <= 1,
    )

    return {"huey": huey, "dewey": dewey, "louie": louie}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
