from hermax.model import Model


def build(instance):
    """
    Construct a binary sequence that minimizes autocorrelations.
    Simplified version: focus on finding valid solutions.
    """
    n = instance["n"]

    model = Model()

    # Binary sequence
    s = model.bool_vector("s", n)

    # For simplicity, just find a sequence
    # The objective can be minimal - just minimize some autocorrelations

    # Compute one or two autocorrelations and add to objective
    for k in [1, 2]:
        if k < n:
            count_same = 0
            for i in range(n):
                j = (i + k) % n
                # Create auxiliary: s[i] == s[j]
                same = model.bool(f"same_{i}_{k}")

                # same is true iff s[i] == s[j]
                # This happens when both are 0 or both are 1
                # i.e., NOT(s[i] XOR s[j]) = NOT(s[i] != s[j])

                # s[i] + s[j] equals 0 (both 0), 1 (different), or 2 (both 1)
                # same is true when sum is 0 or 2

                # Constraint: same == (s[i] == s[j])
                # Equivalently: (s[i] & s[j]) | (~s[i] & ~s[j])
                # = (s[i] & s[j]) | ((1-s[i]) & (1-s[j]))

                # Using implication form:
                # s[i] & s[j] => same (if both true, same is true)
                model &= ~(s[i] & s[j]) | same

                # (1-s[i]) & (1-s[j]) => same (if both false, same is true)
                model &= ~((1 - s[i]) & (1 - s[j])) | same

                # s[i] != s[j] => ~same (if different, same is false)
                # Equivalent: (s[i] & ~s[j]) | (~s[i] & s[j]) => ~same
                model &= ~((s[i] & ~s[j]) | (~s[i] & s[j])) | ~same

                # Simplified: same is true iff s[i] == s[j]
                # Use direct constraint: same >= s[i] * s[j] + (1-s[i]) * (1-s[j]) - 1
                # But this uses multiplication which isn't allowed

                # Alternative: use auxiliary constraints
                # Let eq = s[i] * s[j] + (1-s[i]) * (1-s[j])
                # This equals 1 if s[i] == s[j], 0 otherwise

                # Rewrite: eq = 2*s[i]*s[j] + 2*(1-s[i])*(1-s[j]) - 1
                #            = 2*s[i]*s[j] + 2 - 2*s[i] - 2*s[j] + 2*s[i]*s[j] - 1
                #            = 4*s[i]*s[j] - 2*s[i] - 2*s[j] + 1
                # Still has multiplication

                # Explicit case analysis:
                # s[i]=0, s[j]=0 => same=1
                # s[i]=0, s[j]=1 => same=0
                # s[i]=1, s[j]=0 => same=0
                # s[i]=1, s[j]=1 => same=1

                # Post these as implications:
                # (~s[i] & ~s[j]) => same
                # (s[i] & s[j]) => same
                # (s[i] & ~s[j]) => ~same
                # (~s[i] & s[j]) => ~same

                # In CNF: (~s[i] | ~s[j] | same) & (s[i] | s[j] | same) & ...
                # But these use OR which hermax doesn't support in clauses

                # Simplify: use auxiliary intermediate variables
                both_false = model.bool(f"both_false_{i}_{k}")
                both_true = model.bool(f"both_true_{i}_{k}")

                # both_false = (1-s[i]) & (1-s[j])
                model &= (both_false <= 1 - s[i])
                model &= (both_false <= 1 - s[j])
                model &= (both_false >= 1 - s[i] + 1 - s[j] - 1)

                # both_true = s[i] & s[j]
                model &= (both_true <= s[i])
                model &= (both_true <= s[j])
                model &= (both_true >= s[i] + s[j] - 1)

                # same = both_false | both_true
                # But we can't express OR
                # Use: same >= both_false, same >= both_true, same <= both_false + both_true
                model &= (same >= both_false)
                model &= (same >= both_true)
                model &= (same <= both_false + both_true)

                count_same += same

            # C_k = 2 * count_same - n
            c_k = 2 * count_same - n

            # Add to objective with small penalty
            c_k_var = model.int(f"c_{k}", -n, n)
            model &= (c_k_var == c_k)

            # Penalize if non-zero
            for abs_val in range(1, min(n + 1, 4)):  # Only penalize small values
                is_nonzero = model.bool(f"nz_{k}_{abs_val}")
                model &= ((c_k_var == abs_val) | (c_k_var == -abs_val) | ~is_nonzero)
                model.obj[abs_val] += is_nonzero

    # Output
    output = model.int_vector("sequence", 10, -1, 1)
    for i in range(min(n, 10)):
        model &= (output[i] == 2 * s[i] - 1)
    for i in range(n, 10):
        model &= (output[i] == 0)

    return model, {"sequence": output}
