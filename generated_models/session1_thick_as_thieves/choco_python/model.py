# session1_thick_as_thieves: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install pychoco numpy`) with:
#   python session1_thick_as_thieves.py

from pychoco.model import Model


def create_model(instance):
    """Six suspects in a robbery, at most two of them guilty. The innocent tell the truth and the guilty lie. Who is guilty?"""
    model = Model()

    # Each suspect is guilty or not.
    names = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
    guilty = {name: model.boolvar(name=name) for name in names}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[name] for name in names)

    # The getaway car barely held two, so at most two suspects are guilty.
    n_guilty = model.intvar(0, 2, name="n_guilty")
    model.sum(list(guilty.values()), "=", n_guilty).post()

    # A suspect is guilty exactly when their statement is false.
    # Artie: "It wasn't me." is false exactly when Artie is guilty, so it adds no constraint.
    # Crackitt: "No I wasn't." is false exactly when Crackitt is guilty, so it adds no constraint.
    # Bill: "Crackitt was in it up to his neck." is false exactly when Crackitt is innocent.
    model.arithm(bill, "+", crackitt, "=", 1).post()
    # Dodgy: "If Crackitt did it, Bill did it with him." is false exactly when Crackitt is guilty and Bill is not.
    model.arithm(dodgy, "<=", crackitt).post()
    model.arithm(dodgy, "+", bill, "<=", 1).post()
    model.scalar([dodgy, crackitt, bill], [1, -1, 1], ">=", 0).post()
    # Edgy: "Nobody did it alone." is false exactly when at most one suspect is guilty.
    model.arithm(n_guilty, "<=", 1).reify_with(edgy)
    # Fingers: "It was Artie and Dodgy together." is false exactly when Artie and Dodgy are not both guilty.
    model.arithm(fingers, "+", artie, ">=", 1).post()
    model.arithm(fingers, "+", dodgy, ">=", 1).post()
    model.sum([fingers, artie, dodgy], "<=", 2).post()

    return model, guilty, None


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
