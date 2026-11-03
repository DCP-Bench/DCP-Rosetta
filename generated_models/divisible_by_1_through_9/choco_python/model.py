# divisible_by_1_through_9: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install pychoco numpy`) with:
#   python divisible_by_1_through_9.py

from pychoco.model import Model


def create_model(instance):
    """Find a ten-digit number that uses each digit 0 to 9 exactly once and where,
    for every n, the number formed by its first n digits is divisible by n."""
    # The statement fixes all the data (ten digits, divisors 1 to 10), so the
    # instance has no fields.
    n_digits = 10

    model = Model()

    # digits[i] is the digit at position i of the number, read from left to right
    digits = [model.intvar(0, 9, name=f"digit{i}") for i in range(n_digits)]

    # Each of the digits 0 to 9 is used exactly once.
    model.all_different(digits).post()

    # The number formed by the first n digits is divisible by n.
    # That number is the sum of digits[j] * 10**(n-1-j), which for n = 10 is above
    # 2**31 - 1, the largest value of a Choco integer variable. Replacing each place
    # value 10**(n-1-j) by its remainder modulo n leaves the remainder of the sum
    # modulo n unchanged and keeps the sum below 1000, so `reduced` has the same
    # remainder modulo n as the first n digits.
    for n in range(1, n_digits + 1):
        place_values = [10 ** (n - 1 - j) % n for j in range(n)]
        reduced = model.intvar(0, 9 * sum(place_values), name=f"reduced{n}")
        model.scalar(digits[:n], place_values, "=", reduced).post()
        model.mod(reduced, n, 0).post()

    return model, {"digits": digits}, None


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
