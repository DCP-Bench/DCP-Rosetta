# huey_dewey_louie: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install pychoco numpy`) with:
#   python huey_dewey_louie.py

from pychoco.model import Model


def create_model(instance):
    """Huey, Dewey and Louie are cub scouts questioned by their uncle. They cannot lie,
    so each of their statements is true. Who is guilty?"""
    model = Model()

    # Whether Huey, Dewey and Louie are guilty, in that order
    huey = model.boolvar(name="huey")
    dewey = model.boolvar(name="dewey")
    louie = model.boolvar(name="louie")

    # Huey: Dewey and Louie have equal shares, so if one is guilty, so is the other.
    model.arithm(dewey, "=", louie).post()
    # Dewey: if Huey is guilty, then so is Dewey.
    model.arithm(huey, "<=", dewey).post()
    # Louie: Dewey and Louie are not both guilty.
    model.scalar([dewey, louie], [1, 1], "<=", 1).post()

    return model, {"huey": huey, "dewey": dewey, "louie": louie}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
