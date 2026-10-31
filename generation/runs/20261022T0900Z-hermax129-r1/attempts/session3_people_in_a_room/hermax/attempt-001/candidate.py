from hermax.model import Model


def build(instance):
    # 13 people enter one at a time (the count is fixed by the problem).
    # One Boolean per position: true means a female enters, false a male.
    n_people = 13
    n_males = 4

    m = Model()
    seq = m.bool_vector("sequence", n_people)

    # Exactly 4 males among the 13 people.
    m &= (sum(seq[i] for i in range(n_people)) == n_people - n_males)

    # At every moment with F females and M males in the room: F/M <= 7/3,
    # i.e. 3F <= 7M. With M = k+1-F after k+1 entries this is 10F <= 7(k+1).
    # Zero males with a female present is covered, since 10F <= 0 forces F = 0.
    for k in range(n_people):
        females_so_far = sum(seq[i] for i in range(k + 1))
        m &= (10 * females_so_far <= 7 * (k + 1))

    return m, {"sequence": seq}
