# huey_dewey_louie: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python huey_dewey_louie.py

from pyscipopt import Model


def create_model(instance):
    """Huey, Dewey and Louie are questioned by their uncle about who is guilty.
    Each of them makes one statement, and since these cub scouts cannot tell a lie,
    every statement is true. The model holds the guilt of each cub scout as a 0/1
    variable, and posts the three statements as constraints on those variables.

    The instance file is empty ([]), so the statements fix all the data and
    create_model does not read its argument.
    Returns the model and the three guilt variables.
    """
    model = Model("huey_dewey_louie")

    # Each variable is 1 when that cub scout is guilty and 0 when innocent.
    huey = model.addVar("huey", vtype="B")    # 1 when Huey is guilty
    dewey = model.addVar("dewey", vtype="B")  # 1 when Dewey is guilty
    louie = model.addVar("louie", vtype="B")  # 1 when Louie is guilty

    # Huey: "Dewey and Louie have equal share in it; if one is guilty, so is the other."
    # Both halves say the same thing, so they are one equality: Dewey and Louie are
    # either both guilty or both innocent.
    model.addCons(dewey == louie)

    # Dewey: "If Huey is guilty, then so am I." The conditional is an indicator on
    # Huey's variable: when huey is 1, dewey must be 1.
    model.addConsIndicator(dewey >= 1, binvar=huey)

    # Louie: "Dewey and I are not both guilty." Two 0/1 variables are not both 1
    # exactly when their sum is at most 1.
    model.addCons(dewey + louie <= 1)

    # The problem has no objective: any assignment satisfying the statements is a solution.
    return model, {"dewey": dewey, "huey": huey, "louie": louie}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
