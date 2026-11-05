"""Five statements: statement i says exactly i of the five statements are false; which are true?"""
import hexaly.optimizer as hx


def build(instance):
    n = 5
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # statements[i] = 1 if statement i + 1 ("exactly i + 1 of these statements are false") is true
    statements = [model.bool() for _ in range(n)]
    false_count = n - model.sum(statements)

    # Each statement is true exactly when the number of false statements is what it claims
    for i in range(n):
        model.constraint(statements[i] == (false_count == i + 1))

    return optimizer, {"statements": statements}
