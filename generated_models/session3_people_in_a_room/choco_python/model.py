# session3_people_in_a_room: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install pychoco numpy`) with:
#   python session3_people_in_a_room.py

from pychoco.model import Model


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an entry order
    such that the ratio of females to males in the room is never above 7/3."""
    n_people = 13                    # the number of people
    n_males = 4                      # the number of males among them
    n_females = n_people - n_males   # the number of females among them

    model = Model()

    # sequence[i] is true when the i-th person to enter is female
    sequence = [model.boolvar(name=f"s{i}") for i in range(n_people)]

    # Exactly n_females of the people are female.
    model.sum(sequence, "=", n_females).post()

    # For the first i people, with F females and M = i - F males, F / M <= 7 / 3.
    # Multiplying by 3 gives 3F <= 7M, which is 10F <= 7i.
    for i in range(1, n_people):
        # The room has no ratio before anyone enters, so the check starts at the first entry.
        model.scalar(sequence[:i], [10] * i, "<=", 7 * i).post()

    return model, {"sequence": sequence}, None


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
