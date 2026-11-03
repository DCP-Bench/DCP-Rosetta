# five_statements: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install cpmpy`) with:
#   python five_statements.py

import cpmpy as cp


def create_model(instance):
    """Five statements say that exactly one, exactly two, exactly three,
    exactly four and exactly five of these statements are false. Determine
    which of them is true."""
    # The puzzle states all its statements, so the instance holds no data.
    n = 5

    # statements[i] is true when statement i (numbered from 0) is true
    statements = cp.boolvar(shape=n, name="statements")

    model = cp.Model()
    # Statement i is true exactly when i + 1 of the statements are false.
    num_false = cp.sum(~statements)
    for i in range(n):
        model.add(statements[i] == (num_false == i + 1))

    return model, {"statements": statements}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
