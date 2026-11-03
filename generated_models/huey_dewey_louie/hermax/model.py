# huey_dewey_louie: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install hermax`) with:
#   python huey_dewey_louie.py
#
# Three cub scouts, who cannot lie, make statements about who is guilty.
# Decide who (if any) is guilty: every statement is true, so they must all hold.
from hermax.model import Model


def create_model(instance):
    """Huey, Dewey and Louie make three statements that must all be true, since
    none of them can lie. Decide which of them are guilty."""
    # The statements are fixed by the problem; the instance carries no data.
    m = Model()

    # huey is true when Huey is guilty
    huey = m.bool("huey")
    # dewey is true when Dewey is guilty
    dewey = m.bool("dewey")
    # louie is true when Louie is guilty
    louie = m.bool("louie")

    # Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other.
    m &= (~dewey | louie)
    m &= (dewey | ~louie)

    # Dewey: if Huey is guilty, then so am I.
    m &= (~huey | dewey)

    # Louie: Dewey and I are not both guilty.
    m &= (~dewey | ~louie)

    # There is no objective: the problem asks only who is guilty.
    return m, {"huey": huey, "dewey": dewey, "louie": louie}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
