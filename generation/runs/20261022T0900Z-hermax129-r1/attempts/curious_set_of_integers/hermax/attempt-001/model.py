from hermax.model import Model


def build(instance):
    """
    Find a fifth integer to add to {1, 3, 8, 120} such that
    the product of any two is one less than a perfect square.
    """
    n = instance["n"]  # Should be 5
    max_val = instance["max_val"]  # Search limit

    model = Model()

    # Fixed set (from problem description)
    base_set = [1, 3, 8, 120]

    # New number to find
    new_num = model.int("number", 0, max_val)

    # For each pair in the set, product + 1 must be perfect square
    # Pairs involving the new number
    for b in base_set:
        # new_num * b + 1 = k^2 for some k
        product = new_num * b + 1

        # Find k such that k^2 = product
        # We need to constrain: there exists k where k*k == product

        # k ranges from 0 to sqrt(max_val * max(base_set) + 1)
        k_max = max_val * max(base_set) + 1
        k = model.int(f"sqrt_{new_num}_{b}", 0, int(k_max ** 0.5) + 100)

        # Constraint: k*k == product
        # But we can't use multiplication directly
        # Alternative: create auxiliary constraint
        model &= (k * k == product)

    return model, {"number": new_num}
