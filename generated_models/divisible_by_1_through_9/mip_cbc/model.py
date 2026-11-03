# Problem divisible_by_1_through_9: find a 10 digit number that uses each of the digits 0 to 9
# exactly once and where the number formed by the first n digits of the number is divisible by n.
# The output is the ten digits from left to right (digits). Satisfaction problem; the instance
# carries no fields.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Ten positions (0 is the leftmost digit) and ten digit values 0..9.
    # pick[i][v] = 1 when position i holds digit v; d[i] is that digit.
    pick = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in range(10)] for i in range(10)]
    d = [model.add_var(f"d_{i}", lb=0, ub=9, var_type=mip.INTEGER) for i in range(10)]

    # each position takes exactly one digit
    for i in range(10):
        model.add_constr(mip.xsum(pick[i]) == 1)
        model.add_constr(d[i] == mip.xsum(v * pick[i][v] for v in range(10)))

    # each digit value is used exactly once
    for v in range(10):
        model.add_constr(mip.xsum(pick[i][v] for i in range(10)) == 1)

    # the number is a 10 digit number, so its leading digit is not 0
    model.add_constr(d[0] >= 1)

    # the number formed by the first n digits is divisible by n, for n = 1..10.
    # That number is the sum of 10^(n-1-i) * d[i]. Only its remainder modulo n matters, so each
    # place value is replaced by its remainder modulo n, which keeps every coefficient below 10.
    # With the full place values (up to 10^9) CBC did not finish the search within 180 s.
    # The reduced sum is then n times an integer k.
    for n in range(1, 11):
        weights = [pow(10, n - 1 - i, n) for i in range(n)]
        k = model.add_var(f"k_{n}", lb=0, ub=sum(9 * w for w in weights) // n, var_type=mip.INTEGER)
        model.add_constr(mip.xsum(w * d[i] for i, w in enumerate(weights)) == n * k)

    return model, {"digits": d}
