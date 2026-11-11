# initials_queue: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python initials_queue.py

from docplex.mp.model import Model


def create_model(instance):
    """Initials queue: ten people queue with initials that are alphabetically ordered pairs of
    distinct letters from A..E, no two alike and no one sharing a letter with the person in front.
    BE is first, CD second and BD last. Find the queue."""
    n = 10  # the number of people in the queue
    n_letters = 5  # the letters A..E
    A, B, C, D, E = range(n_letters)  # the letters are numbered 0..4, as in the output
    letters = range(n_letters)
    # Every alphabetically ordered pair of distinct letters a < b.
    pairs = [(a, b) for a in letters for b in letters if a < b]
    places = range(n)

    model = Model("initials_queue")

    # has[i, p] is 1 when person i has initials pairs[p]; each person has one pair.
    has = {(i, p): model.binary_var(name=f"person_{i}_pair_{p}") for i in places
           for p in range(len(pairs))}
    model.add_constraints(model.sum(has[i, p] for p in range(len(pairs))) == 1 for i in places)

    # No two people have the same initials.
    model.add_constraints(model.sum(has[i, p] for i in places) <= 1 for p in range(len(pairs)))

    def uses(i, letter):
        # 1 when person i's initials contain the letter.
        return model.sum(has[i, p] for p, pair in enumerate(pairs) if letter in pair)

    # No one shares a letter with the person in front.
    model.add_constraints(uses(i, letter) + uses(i + 1, letter) <= 1
                          for i in range(n - 1) for letter in letters)

    # BE is at the front, CD right behind, and BD at the end.
    model.add_constraint(has[0, pairs.index((B, E))] == 1)
    model.add_constraint(has[1, pairs.index((C, D))] == 1)
    model.add_constraint(has[n - 1, pairs.index((B, D))] == 1)

    # queue[i] is the pair of initials of person i, read from the chosen pair.
    queue = [[model.sum(pair[s] * has[i, p] for p, pair in enumerate(pairs) if pair[s])
              for s in range(2)] for i in places]

    return model, {"queue": queue}


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
