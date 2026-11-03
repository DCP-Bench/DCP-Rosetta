# initials_queue: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install pychoco numpy`) with:
#   python initials_queue.py

from pychoco.model import Model

# Letters are numbers: A=0, B=1, C=2, D=3, E=4.
A, B, C, D, E = range(5)


def create_model(instance):
    """Ten mathematicians stand in a queue. Each has two distinct initials from A to E in
    alphabetical order, nobody has the same initials as another, and nobody shares a
    letter with the person in front. BE is at the front, CD right behind, and BD at the
    end. What are the initials of the ten people, from the front?"""
    n_people = 10  # people in the queue

    model = Model()

    # The allowed initials: pairs of distinct letters in alphabetical order.
    pairs = [(x, y) for x in range(A, E + 1) for y in range(x + 1, E + 1)]
    # Each allowed pair with its number, so that the numbers tell people apart by their initials.
    pair_rows = [[x, y, k] for k, (x, y) in enumerate(pairs)]

    # queue[i][k] is the k-th initial of the person at place i, counting from the front.
    queue = [[model.intvar(A, E, name=f"queue_{i}_{k}") for k in range(2)]
             for i in range(n_people)]
    # pair_no[i] is the number of the initials of the person at place i.
    pair_no = [model.intvar(0, len(pairs) - 1, name=f"pair_no_{i}") for i in range(n_people)]

    # Each person's initials are an allowed pair, with its number.
    for i in range(n_people):
        model.table(queue[i] + [pair_no[i]], pair_rows).post()
    # Nobody has the same initials as another person.
    model.all_different(pair_no).post()

    # Nobody shares a letter with the person in front of them.
    for i in range(n_people - 1):
        for x in queue[i]:
            for y in queue[i + 1]:
                model.arithm(x, "!=", y).post()

    # BE is at the front, CD right behind it, and BD at the end of the queue.
    known = {0: (B, E), 1: (C, D), n_people - 1: (B, D)}
    # The people at these places have the given initials.
    for i, (x, y) in known.items():
        model.arithm(queue[i][0], "=", x).post()
        model.arithm(queue[i][1], "=", y).post()

    return model, {"queue": queue}, None


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
