# five_statements: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install hermax`) with:
#   python five_statements.py

from hermax.model import Model


def create_model(instance):
    """Decide which of five self-referential statements are true. Statement k says that
    exactly k of the five statements are false, so a statement is true exactly when that
    count condition holds for the whole set. The problem has a fixed data set and no
    instance fields, so the model does not read the instance argument."""
    m = Model()

    # statements[k - 1] is true when statement k holds
    statements = m.bool_vector("statement", 5)

    # Statement k says exactly k statements are false, which is the same as exactly
    # 5 - k statements being true. Each statement is reified to its own count condition:
    # the statement is true if and only if exactly 5 - k of the five statements are true.
    for k in range(1, 6):
        m &= (sum(statements) == 5 - k).iff(statements[k - 1])

    return m, {"statements": statements}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
