# five_statements: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python five_statements.py

from docplex.mp.model import Model


def create_model(instance):
    """Five statements say: exactly one of these statements is false, exactly two are false, and
    so on up to exactly five. Determine which of the statements are true."""
    n = 5  # the number of statements
    model = Model("five_statements")

    # statements[i] is 1 when statement i + 1 is true.
    statements = [model.binary_var(name=f"statement_{i + 1}") for i in range(n)]

    # Statement i + 1 is true exactly when i + 1 statements are false, that is when
    # n - (i + 1) statements are true.
    for i in range(n):
        model.add_equivalence(statements[i], model.sum(statements) == n - (i + 1))

    return model, {"statements": statements}


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
