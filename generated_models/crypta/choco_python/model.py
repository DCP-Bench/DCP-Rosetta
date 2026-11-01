# crypta: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install pychoco numpy`) with:
#   python crypta.py

from pychoco.model import Model

# The two addends and their sum, as written in the puzzle.
FIRST_ADDEND = "BAIJJAJIIAHFCFEBBJEA"
SECOND_ADDEND = "DHFGABCDIDBIFFAGFEJE"
SUM = "GJEGACDDHFAFJBFIHEEF"


def create_model(instance):
    """Cryptarithm: give each letter A to J a different digit so that the first addend
    plus the second addend equals the sum, with no number starting with zero."""
    # The first letters of the three numbers.
    first_letters = {FIRST_ADDEND[0], SECOND_ADDEND[0], SUM[0]}

    model = Model()

    # The digit of each letter. The first letters of the three numbers are not zero.
    digit = {letter: model.intvar(1 if letter in first_letters else 0, 9, name=letter)
             for letter in "ABCDEFGHIJ"}

    # All letters stand for different digits.
    model.all_different(list(digit.values())).post()

    # carry[c] is the carry into the column c places from the units column. Nothing
    # is carried into the units column or out of the leading column.
    width = len(SUM)
    carry = ([model.intvar(0, 0)] + [model.intvar(0, 1) for _ in range(width - 1)]
             + [model.intvar(0, 0)])

    # Column by column from the units, the two addend digits and the carry in add up to
    # the sum digit plus ten times the carry out.
    for c, (top, bottom, total) in enumerate(
            zip(reversed(FIRST_ADDEND), reversed(SECOND_ADDEND), reversed(SUM))):
        model.scalar([digit[top], digit[bottom], carry[c], digit[total], carry[c + 1]],
                     [1, 1, 1, -1, -10], "=", 0).post()

    return model, digit, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
