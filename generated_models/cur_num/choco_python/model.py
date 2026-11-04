# cur_num: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install pychoco numpy`) with:
#   python cur_num.py

from pychoco.model import Model


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    model = Model()

    # The peculiar number, between 1 and 10000.
    peculiar = model.intvar(1, 10000, name="peculiar")
    # peculiar + 1, which is a square number
    plus_one = model.intvar(1, 10000, name="plus_one")
    # the square root of plus_one
    root_plus_one = model.intvar(1, 10000, name="root_plus_one")
    # half of peculiar
    half = model.intvar(1, 10000, name="half")
    # half + 1, which is a square number
    half_plus_one = model.intvar(1, 10000, name="half_plus_one")
    # the square root of half_plus_one
    root_half_plus_one = model.intvar(1, 10000, name="root_half_plus_one")

    # The known example 48 does not count.
    model.arithm(peculiar, "!=", 48).post()

    # Adding 1 to the peculiar number gives a square number.
    model.scalar([peculiar, plus_one], [1, -1], "=", -1).post()
    model.square(plus_one, root_plus_one).post()

    # Half of the peculiar number, plus 1, gives a square number too.
    model.scalar([peculiar, half], [1, -2], "=", 0).post()
    model.scalar([half, half_plus_one], [1, -1], "=", -1).post()
    model.square(half_plus_one, root_half_plus_one).post()

    return model, {"peculiar": peculiar}, None


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
