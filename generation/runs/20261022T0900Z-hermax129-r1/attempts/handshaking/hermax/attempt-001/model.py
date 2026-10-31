"""Handshaking - find how many hands Hilary shook given unique handshake counts.

With num_couples invited couples (plus Hilary and Jocelyn), each person can shake
hands with 0 to 2*num_couples people (max is everyone except themselves and spouse).
All people except Jocelyn reported different handshake counts.
"""

from hermax.model import Model


def build(instance):
    num_couples = instance["num_couples"]

    # Total people: num_couples invited couples + Hilary and Jocelyn = 2*num_couples + 2
    # People who report handshakes: everyone except Jocelyn = 2*num_couples + 1

    num_people = 2 * num_couples + 2
    num_reporters = num_people - 1  # Everyone except Jocelyn
    max_handshakes = num_people - 2  # Can't shake hands with spouse and self

    m = Model()

    # handshakes[i] = number of hands person i has shaken
    # We have 2*num_couples + 1 people reporting (indices 0 to 2*num_couples)
    # Person 0 = Hilary, Person 1 = Jocelyn's spouse, ..., Person 2*num_couples = last person

    handshakes = m.int_vector("handshakes", num_reporters, 0, max_handshakes)

    # All handshake counts must be different
    m &= handshakes.all_different()

    # Constraint: the person who shook hands with k people and the person who shook
    # hands with 2*num_couples - k people must be married
    # This is the key insight of the handshaking problem

    # Create couples mapping: assume even indices are husbands, odd indices are wives
    # Person i is married to Person (i XOR 1) - but we need linear constraints

    # Mapping: persons 0,1 are a couple; 2,3 are couple; etc.
    # But actually, we need to figure out the pairing from the constraint

    # Simpler constraint: for each value k from 0 to max_handshakes-1,
    # if someone shook k hands and someone else shook (max_handshakes - k) hands,
    # they must be married

    # Create married_to[i] = person married to person i
    # We need to determine this from the constraints

    # Key constraint: if person i shook hands with k people, and person i is married to person j,
    # then person j must have shaken hands with (max_handshakes - k) people
    # This is because they can't shake hands with each other or themselves

    # Let's use a different approach: create variables for the mapping
    married_to = m.int_vector("married_to", num_reporters, 0, num_reporters - 1)

    # Constraint: if i is married to j, then j is married to i
    for i in range(num_reporters):
        j = married_to[i]
        m &= (married_to[j] == i)

    # Nobody is married to themselves
    for i in range(num_reporters):
        m &= (married_to[i] != i)

    # Constraint: if person i shook k hands and person j (married to i) shook m hands,
    # then k + m = max_handshakes
    for i in range(num_reporters):
        j = married_to[i]
        m &= (handshakes[i] + handshakes[j] == max_handshakes)

    # Hilary is person 0 - output the number of hands Hilary shook
    hil = handshakes[0]

    outputs = {
        "hil": hil,
    }

    return m, outputs
