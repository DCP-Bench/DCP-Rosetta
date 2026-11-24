# csplib_024_langford: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_024_langford.py csplib_024_langford.json

from docplex.mp.model import Model


def create_model(instance):
    """Langford's problem: arrange two copies of 1..k in a row so that the two copies of i have exactly i numbers between them."""
    k = instance["k"]  # the numbers 1..k each appear twice
    length = 2 * k  # both sets of numbers fill the sequence
    numbers = range(1, k + 1)

    model = Model("langford")

    # starts[i, p] is 1 when the first copy of i is at position p; the second
    # copy is then at p + i + 1, which must still be in the row.
    starts = {(i, p): model.binary_var(name=f"starts_{i}_{p}") for i in numbers for p in range(length - i - 1)}

    # Each number is placed exactly once (its pair of copies).
    model.add_constraints(model.sum(v for (j, p), v in starts.items() if j == i) == 1 for i in numbers)

    # covers[q] lists the placements that put a copy at position q.
    covers = {q: [] for q in range(length)}
    for (i, p) in starts:
        covers[p].append((i, p))
        covers[p + i + 1].append((i, p))

    # Every position of the row holds exactly one copy.
    model.add_constraints(model.sum(starts[key] for key in covers[q]) == 1 for q in range(length))

    # sol[q] is the number at position q, read back from the placements.
    sol = [model.sum(i * starts[i, p] for (i, p) in covers[q]) for q in range(length)]
    return model, {"sol": sol}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
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
