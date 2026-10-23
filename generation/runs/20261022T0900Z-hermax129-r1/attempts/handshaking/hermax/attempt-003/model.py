from hermax.model import Model


def build(instance):
    # Hilary and Jocelyn are a couple, plus the invited couples. Person 0 is
    # Hilary, person 1 is Jocelyn, and persons 2k and 2k+1 are spouses.
    n = instance["num_couples"]
    people = 2 * (n + 1)
    max_hands = people - 2

    m = Model()

    # One Boolean per possible handshake. Nobody shakes hands with themselves
    # or with their spouse, and a handshake is shared by both people.
    shake = {}
    for i in range(people):
        for j in range(i + 1, people):
            if j == (i ^ 1):
                continue
            shake[(i, j)] = m.bool(f"shake_{i}_{j}")

    def edge(i, j):
        return shake[(min(i, j), max(i, j))]

    # Each person's hands are the handshakes they take part in. Jocelyn asks
    # the question, so the answers come from everyone else.
    answers = m.int_vector("answer", people - 1, 0, max_hands)
    persons = [p for p in range(people) if p != 1]
    for k, p in enumerate(persons):
        lits = [edge(p, q) for q in range(people) if q != p and q != (p ^ 1)]
        m &= (answers[k] == sum(lits))

    # All the answers are different. With 2n+1 answers in 0..2n, every value
    # from 0 to 2n is then given by exactly one person.
    m &= answers.all_different()
    for v in range(max_hands + 1):
        m &= (sum(answers[k] == v for k in range(len(persons))) == 1)

    outputs = {"hil": answers[0]}
    return m, outputs
