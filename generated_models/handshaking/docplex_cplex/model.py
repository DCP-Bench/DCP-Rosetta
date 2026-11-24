# handshaking: a CPLEX (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python handshaking.py handshaking.json

from docplex.mp.model import Model


def create_model(instance):
    """Hilary and Jocelyn are married and invite a number of couples for dinner; everybody shakes
    hands with some of the others, but nobody with themselves or their spouse. Jocelyn asks everyone
    else how many hands they shook, and all the answers are different. How many did Hilary shake?"""
    n = 2 + 2 * instance["num_couples"]  # the invited couples plus the hosts Hilary and Jocelyn
    people = range(n)
    hilary, jocelyn = 0, 1  # the two hosts, who are married
    # Spouses sit next to each other: 0 and 1, 2 and 3, and so on.
    spouse = [p + 1 if p % 2 == 0 else p - 1 for p in people]

    model = Model("handshaking")

    # shake[i, j], for i < j, is 1 when i and j shook hands; nobody shakes hands
    # with themselves or their spouse, so those pairs have no variable at all.
    pairs = [(i, j) for i in people for j in range(i + 1, n) if j != spouse[i]]
    shake = {pair: model.binary_var(name=f"shake_{pair[0]}_{pair[1]}") for pair in pairs}

    def hands(p):
        return model.sum(shake[i, j] for (i, j) in pairs if p in (i, j))

    # Jocelyn asks everyone else and all the answers differ. Those are n - 1 people with
    # counts in 0..n-2, so every count occurs exactly once.
    others = [p for p in people if p != jocelyn]
    counts = range(n - 1)
    # has[p, c] is 1 when person p shook c hands
    has = model.binary_var_matrix(others, counts, name="has")
    for p in others:
        model.add_constraint(model.sum(has[p, c] for c in counts) == 1, ctname=f"one_count_{p}")
        model.add_constraint(hands(p) == model.sum(c * has[p, c] for c in counts), ctname=f"count_{p}")
    for c in counts:
        model.add_constraint(model.sum(has[p, c] for p in others) == 1, ctname=f"distinct_{c}")

    # hil is the number of hands Hilary shook. It is a variable of its own so that
    # the declared output is this one number, not every handshake behind it.
    hil = model.integer_var(0, n - 2, name="hil")  # n - 2: not with themselves or their spouse
    model.add_constraint(hil == hands(hilary), ctname="hilary")

    return model, {"hil": hil}


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
