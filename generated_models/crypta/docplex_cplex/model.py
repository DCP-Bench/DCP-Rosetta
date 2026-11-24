# crypta: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python crypta.py

from docplex.mp.model import Model


def create_model(instance):
    """Cryptarithmetic puzzle: solve BAIJJAJIIAHFCFEBBJEA + DHFGABCDIDBIFFAGFEJE = GJEGACDDHFAFJBFIHEEF,
    where all letters are distinct digits from 0 to 9, and the first letter of each number
    cannot be zero."""
    # the two numbers added and their sum, as words of letters
    addend_1, addend_2, total = "BAIJJAJIIAHFCFEBBJEA", "DHFGABCDIDBIFFAGFEJE", "GJEGACDDHFAFJBFIHEEF"
    letters = "ABCDEFGHIJ"  # the letters of the puzzle
    digits = range(10)

    model = Model("crypta")

    # is_digit[c, d] is 1 when letter c stands for digit d; each letter is one digit and the
    # letters are all different digits.
    is_digit = {(c, d): model.binary_var(name=f"{c}_is_{d}") for c in letters for d in digits}
    model.add_constraints(model.sum(is_digit[c, d] for d in digits) == 1 for c in letters)
    model.add_constraints(model.sum(is_digit[c, d] for c in letters) <= 1 for d in digits)

    # value[c] is the digit that letter c stands for
    value = {c: model.sum(d * is_digit[c, d] for d in digits) for c in letters}

    # The first letter of each number is not zero.
    model.add_constraints(value[number[0]] >= 1 for number in (addend_1, addend_2, total))

    # The addition holds: the two numbers add up to the total. CPLEX cannot keep the 20-digit
    # numbers as one sum (coefficients up to 10^19 are beyond the integers a double holds
    # exactly), so the columns, counted from the right, are cut into blocks of at most 7 digits.
    # In each block the addends plus the carry in from the block below equal the block of the
    # total plus 10^(block width) times the carry out into the block above.
    blocks = [(0, 7), (7, 14), (14, 20)]  # the columns [first, last) of each block

    def block_value(number, first, last):
        """The number written by the digits of columns first .. last - 1 of the word."""
        return model.sum(10 ** (column - first) * value[number[-1 - column]]
                         for column in range(first, last))

    # carry[k] is 1 when the sum of block k carries one into block k + 1
    carry = [model.binary_var(name=f"carry_{k}") for k in range(len(blocks) - 1)]
    for k, (first, last) in enumerate(blocks):
        carry_in = carry[k - 1] if k > 0 else 0
        carry_out = 10 ** (last - first) * carry[k] if k < len(carry) else 0
        model.add_constraint(block_value(addend_1, first, last) + block_value(addend_2, first, last)
                             + carry_in == block_value(total, first, last) + carry_out)

    return model, value


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
