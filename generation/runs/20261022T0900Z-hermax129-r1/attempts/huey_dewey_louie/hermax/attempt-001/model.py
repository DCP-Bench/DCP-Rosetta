from hermax.model import Model


def build(instance):
    """
    Logic puzzle: Huey, Dewey, and Louie are questioned about guilt.
    All three tell the truth. Find who is guilty.

    Constraints from their statements:
    1. Huey: Dewey and Louie have equal share (both guilty or both innocent)
    2. Dewey: If Huey is guilty, then so am I (huey => dewey)
    3. Louie: Dewey and I are not both guilty (~(dewey & louie))
    """
    m = Model()

    # Variables: True if guilty, False if innocent
    huey = m.bool("huey")
    dewey = m.bool("dewey")
    louie = m.bool("louie")

    # Constraint 1: Huey's statement - Dewey and Louie have equal share
    # dewey == louie (either both true or both false)
    # This means: (dewey => louie) AND (louie => dewey)
    m &= (~dewey | louie)  # dewey => louie
    m &= (~louie | dewey)  # louie => dewey

    # Constraint 2: Dewey's statement - If Huey is guilty, then so am I
    # huey => dewey
    m &= (~huey | dewey)

    # Constraint 3: Louie's statement - Dewey and I are not both guilty
    # ~(dewey & louie)
    m &= (~dewey | ~louie)

    return m, {"huey": huey, "dewey": dewey, "louie": louie}
