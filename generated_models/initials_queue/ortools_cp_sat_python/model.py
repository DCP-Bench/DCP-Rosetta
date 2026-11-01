# initials_queue: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install ortools`) with:
#   python initials_queue.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Ten mathematicians stand in a queue, each with two distinct initials from A to E in
    alphabetical order, no two people with the same initials, and nobody sharing a letter
    with the person in front. BE is at the front, CD right behind and BD at the end; what
    are the initials of the ten people, from the front?"""
    n_people = 10  # people in the queue
    n_letters = 5  # the letters A to E

    model = cp_model.CpModel()

    # Letters are numbers: A=0, B=1, C=2, D=3, E=4.
    # queue[i][k]: the k-th initial of the person at place i, counting from the front
    queue = [[model.new_int_var(0, n_letters - 1, f"queue_{i}_{k}") for k in range(2)]
             for i in range(n_people)]

    # The two initials of each person are distinct and in alphabetical order.
    for i in range(n_people):
        model.add(queue[i][0] < queue[i][1])

    # The code of the person at each place: the two initials read as one number.
    codes = []
    for i in range(n_people):
        code = model.new_int_var(0, n_letters * n_letters - 1, f"code_{i}")
        model.add(code == n_letters * queue[i][0] + queue[i][1])
        codes.append(code)
    # Nobody has the same initials as another person.
    model.add_all_different(codes)

    # Nobody shares a letter with the person in front of them.
    for i in range(n_people - 1):
        for a in range(2):
            for b in range(2):
                model.add(queue[i][a] != queue[i + 1][b])

    # BE is at the front, CD right behind, and BD at the end of the queue.
    model.add(queue[0][0] == 1)
    model.add(queue[0][1] == 4)
    model.add(queue[1][0] == 2)
    model.add(queue[1][1] == 3)
    model.add(queue[n_people - 1][0] == 1)
    model.add(queue[n_people - 1][1] == 3)

    return model, {"queue": queue}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
