# five_statements: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python five_statements.py

from pycsp3 import *


def create_model(instance):
    """Determine which of the following statements is true.
    - Exactly one of these statements is false.
    - Exactly two of these statements are false.
    - Exactly three of these statements are false.
    - Exactly four of these statements are false.
    - Exactly five of these statements are false."""
    n_statements = 5

    # statements[k - 1] is 1 when statement k is true, 0 when it is false
    statements = VarArray(size=n_statements, dom={0, 1})

    satisfy(
        # Statement k is true exactly when the number of false statements is k,
        # that is when the number of true statements is n_statements - k.
        [statements[k - 1] == (Sum(statements) == n_statements - k) for k in range(1, n_statements + 1)]
    )

    return {"statements": statements}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", values(variable))
    else:
        print("No solution:", status())
