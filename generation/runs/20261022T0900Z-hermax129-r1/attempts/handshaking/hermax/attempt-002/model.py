from hermax.model import Model


def build(instance):
    """Handshaking puzzle.

    Find hand shake counts for 2n people where all counts are different.
    Constraints: nobody shakes with self or spouse.
    """
    num_couples = instance["num_couples"]
    n = num_couples + 1
    total_people = 2 * n

    model = Model()

    # Variables: x[i] = hands shaken by person i
    # Each person can shake at most 2n-2 hands (not self, not spouse)
    x = model.int_vector("x", total_people, 0, total_people - 1)

    # All counts must be different
    model &= x.all_different()

    # Key insight: in the handshaking puzzle, if person i shakes k hands,
    # their spouse cannot also shake k hands (different people have different counts).
    # Moreover, each person can shake with at most 2n-2 others.
    # For all counts to be different with n couples, one approach is:
    # - One couple has counts that differ significantly
    # - The other couples have complementary counts

    # Specific constraint for the puzzle: if person i shakes k hands,
    # and the spouse shakes j hands, they satisfy certain relationship.
    # The classic puzzle has the solution based on:
    # Person who shakes 2n-2 has spouse who shakes 0 (didn't shake with anyone)
    # Person who shakes 2n-3 has spouse who shakes 1, etc.
    # EXCEPT: the person asking (Jocelyn) doesn't count themselves or Hilary

    # Let's model: person 0 = Hilary, person 1 = Jocelyn
    # For couples 1 to n-1: spouses should have complementary counts
    for couple_idx in range(1, n):
        p1 = 2 * couple_idx
        p2 = 2 * couple_idx + 1
        # These couples have complementary shake counts
        model &= (x[p1] + x[p2] == 2 * n - 2)

    # Hilary's count is not constrained by this (except all_different)

    return model, {"hil": x[0]}
