# initials_queue: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install cpmpy`) with:
#   python initials_queue.py

import cpmpy as cp


def create_model(instance):
    """Ten mathematicians stand in a queue. Each has two distinct initials from A..E in
    alphabetical order, nobody has the same initials as another, and nobody shares a
    letter with the person in front. BE is at the front, CD right behind, BD at the end."""
    # The puzzle states its own queue, so the instance is empty.
    n = 10  # people in the queue

    # Letters are numbers: A=0, B=1, C=2, D=3, E=4.
    # queue[i] holds the two initials of the person at place i, front first.
    queue = cp.intvar(0, 4, shape=(n, 2), name="queue")

    model = cp.Model()

    # The two initials of each person are distinct and in alphabetical order.
    model.add(queue[:, 0] < queue[:, 1])

    # Nobody has the same initials as another person.
    for i in range(n):
        for j in range(i + 1, n):
            model.add((queue[i, 0] != queue[j, 0]) | (queue[i, 1] != queue[j, 1]))

    # Nobody shares a letter with the person in front of them.
    for i in range(n - 1):
        for a in range(2):
            for b in range(2):
                model.add(queue[i, a] != queue[i + 1, b])

    # BE is at the front, CD right behind, and BD at the end of the queue.
    model.add(queue[0, 0] == 1)
    model.add(queue[0, 1] == 4)
    model.add(queue[1, 0] == 2)
    model.add(queue[1, 1] == 3)
    model.add(queue[n - 1, 0] == 1)
    model.add(queue[n - 1, 1] == 3)

    return model, {"queue": queue}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
