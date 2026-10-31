from hermax.model import Model


def build(instance):
    """
    Age changing problem: find two ages (m, h) such that:
    - Applying the four operations (+2, /8, -3, *7) in some order to m gives h
    - Applying the same four operations in a different order to h gives m

    Fixed constants: ages in range [16, 120], operations are (+2, /8, -3, *7)
    """
    m = Model()

    # Ages are in range 16 to 120
    my_age = m.int("m", 16, 120)
    husband_age = m.int("h", 16, 120)

    # Two permutations of operations (0=+2, 1=/8, 2=-3, 3=*7)
    perm1 = m.int_vector("perm1", 4, 0, 3)
    perm2 = m.int_vector("perm2", 4, 0, 3)

    # Intermediate values when applying operations to my age
    hlist = m.int_vector("hlist", 5, 1, 1000)
    # Intermediate values when applying operations to husband's age
    mlist = m.int_vector("mlist", 5, 1, 1000)

    # Starting values
    m &= (hlist[0] == my_age)
    m &= (mlist[0] == husband_age)

    # Ending values
    m &= (hlist[4] == husband_age)
    m &= (mlist[4] == my_age)

    # All operations used exactly once in each permutation
    m &= perm1.all_different()
    m &= perm2.all_different()

    # Permutations must be different (symmetry breaking with lexicographic ordering)
    m &= perm1.lexicographic_less_than(perm2)

    # Apply operations for permutation 1 (my_age -> husband_age)
    for i in range(4):
        op = perm1[i]
        old = hlist[i]
        new = hlist[i + 1]

        # op == 0: new = old + 2
        m &= ((op == 0).implies(new == old + 2))
        # op == 1: 8 * new = old (division)
        m &= ((op == 1).implies(8 * new == old))
        # op == 2: new = old - 3
        m &= ((op == 2).implies(new == old - 3))
        # op == 3: new = old * 7
        m &= ((op == 3).implies(new == old * 7))

    # Apply operations for permutation 2 (husband_age -> my_age)
    for i in range(4):
        op = perm2[i]
        old = mlist[i]
        new = mlist[i + 1]

        # op == 0: new = old + 2
        m &= ((op == 0).implies(new == old + 2))
        # op == 1: 8 * new = old (division)
        m &= ((op == 1).implies(8 * new == old))
        # op == 2: new = old - 3
        m &= ((op == 2).implies(new == old - 3))
        # op == 3: new = old * 7
        m &= ((op == 3).implies(new == old * 7))

    return m, {"m": my_age, "h": husband_age}
