from hermax.model import Model


def build(instance):
    num_cows = instance["num_cows"]
    num_sons = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]

    # Cow c (numbered c + 1) gives c + 1 litres of milk.
    total_milk = num_cows * (num_cows + 1) // 2
    milk_per_son = total_milk // num_sons

    m = Model()
    cow = m.int_vector("cow", num_cows, 0, num_sons - 1)
    x = m.bool_matrix("x", num_cows, num_sons)

    # Link each son-index variable to its Boolean indicator.
    for c in range(num_cows):
        for s in range(num_sons):
            m &= (cow[c] == s).iff(x[c][s])

    # Every cow goes to exactly one son.
    for c in range(num_cows):
        m &= x.row(c).exactly_one()

    # Each son gets the number of cows given in the distribution.
    for s in range(num_sons):
        m &= (sum(x[c][s] for c in range(num_cows)) == cows_per_son[s])

    # The milk of each son is the same: total milk divided by the number of sons.
    for s in range(num_sons):
        m &= (sum((c + 1) * x[c][s] for c in range(num_cows)) == milk_per_son)

    return m, {"cow_assignments": cow}
