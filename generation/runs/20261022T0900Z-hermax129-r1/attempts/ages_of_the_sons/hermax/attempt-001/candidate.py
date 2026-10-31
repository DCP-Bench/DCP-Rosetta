"""
Ages of the sons: find three ages that multiply to 36,
sum to an ambiguous value, with unique oldest son.

The puzzle logic:
- Product of ages = 36: enumerate valid factorizations
- Sum must be ambiguous (multiple factorizations with same sum)
- "Oldest has blue eyes" means there's a unique oldest son
  (no tie for maximum age)
- The only ambiguous sum is 13: (1,6,6) and (2,2,9)
- Only (2,2,9) has a unique oldest: 9 != 6 or 6
- Answer in descending order: A1=9, A2=2, A3=2
"""

from hermax.model import Model


def build(instance):
    m = Model()

    # All factorizations of 36 as (A1, A2, A3) with A1 >= A2 >= A3
    valid_triples = [
        (36, 1, 1),
        (18, 2, 1),
        (12, 3, 1),
        (9, 4, 1),
        (9, 2, 2),
        (6, 6, 1),
        (6, 3, 2),
        (4, 3, 3),
    ]

    # One Boolean for each triple
    options = m.bool_vector("option", len(valid_triples))

    # Exactly one triple is selected
    m &= options.exactly_one()

    # The selected ages are represented as integers
    A1 = m.int("A1", 1, 36)
    A2 = m.int("A2", 1, 36)
    A3 = m.int("A3", 1, 36)

    # Link the Boolean selections to the age values
    for i, (a1, a2, a3) in enumerate(valid_triples):
        # If this option is chosen, then the ages match
        m &= (~options[i] | (A1 == a1))
        m &= (~options[i] | (A2 == a2))
        m &= (~options[i] | (A3 == a3))

    # The sum must be ambiguous: it must be 13
    # (the only sum with multiple factorizations: (1,6,6) and (2,2,9))
    m &= (A1 + A2 + A3 == 13)

    # Unique oldest son: the maximum age appears only once
    # This rules out (1,6,6) where two sons are 6, and accepts (2,2,9)
    m &= (A1 > A2)

    return m, {"A1": A1, "A2": A2, "A3": A3}
