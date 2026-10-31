from hermax.model import Model


def build(instance):
    """
    Construct a binary sequence of length n that minimizes autocorrelations.
    Each bit is +1 or -1. With periodic boundary conditions, the k-th autocorrelation is:
    C_k = sum_{i=0}^{n-1} S_i * S_{(i+k) mod n}

    Objective: minimize the sum of squares of autocorrelations.
    """
    n = instance["n"]

    model = Model()

    # Create binary sequence: s[i] is 0 (representing -1) or 1 (representing +1)
    s = model.bool_vector("s", n)

    # For autocorrelation: C_k = sum_{i} s_val[i] * s_val[(i+k) % n]
    # where s_val[i] = 2*s[i] - 1 (so either -1 or +1)
    # = sum_{i} (2*s[i] - 1) * (2*s[(i+k)%n] - 1)
    # = sum_{i} (4*s[i]*s[(i+k)%n] - 2*s[i] - 2*s[(i+k)%n] + 1)
    # But we can't multiply s[i] * s[(i+k)%n] directly

    # Alternative: if s[i] == s[(i+k)%n], product is +1; else -1
    # Count same: count of i where s[i] == s[(i+k)%n]
    # C_k = 2*count_same - n

    # Compute autocorrelations
    c_k_vars = []

    for k in range(1, n):
        # For each k, count how many positions have s[i] == s[(i+k) % n]
        # Use auxiliary variables

        count_expr = 0
        for i in range(n):
            # Create auxiliary: equal_ik = (s[i] == s[(i+k) % n])
            equal_ik = model.bool(f"eq_{i}_{k}")

            # Constraint: equal_ik == (s[i] == s[(i+k) % n])
            # This is true when both are 0 or both are 1, i.e., XOR is false
            # equal_ik == NOT(s[i] XOR s[(i+k)%n])
            # equal_ik == (s[i] + s[(i+k)%n] != 1)
            # Equal only when sum is 0 or 2, i.e., NOT (sum == 1)

            sum_ik = s[i] + s[(i + k) % n]  # This is 0, 1, or 2

            # Create boolean: sum_eq_1 = (sum_ik == 1)
            sum_eq_1 = model.bool(f"sum_eq_1_{i}_{k}")
            # sum_eq_1 is true iff sum_ik == 1
            # We can constrain this, but need auxiliary variables

            # Instead: equal_ik is true iff sum_ik != 1
            # equal_ik = (sum_ik == 0) | (sum_ik == 2)
            # But we can't directly check equality in clauses

            # Alternative: use auxiliary int variable
            sum_var = model.int(f"sum_{i}_{k}", 0, 2)
            model &= (sum_var == sum_ik)

            # Now: equal_ik should be true iff sum_var != 1
            # Create: not_eq_1 = (sum_var != 1)
            not_eq_1 = model.bool(f"not_eq_1_{i}_{k}")

            # not_eq_1 is true iff sum_var is 0 or 2
            # We can use: if sum_var == 0, not_eq_1 = true; if sum_var == 1, not_eq_1 = false; if sum_var == 2, not_eq_1 = true
            # This is complex to encode directly. Let me use a different approach.

            # Alternative: equal_ik is true iff s[i] == s[(i+k)%n]
            # equal_ik = (s[i] & s[(i+k)%n]) | (~s[i] & ~s[(i+k)%n])
            # = (s[i] & s[(i+k)%n]) | ((1-s[i]) & (1-s[(i+k)%n]))
            # = (s[i] & s[(i+k)%n]) | (1 - s[i] - s[(i+k)%n] + s[i] + s[(i+k)%n])
            # = (s[i] & s[(i+k)%n]) | (1 - s[i] - s[(i+k)%n] + s[i] + s[(i+k)%n])
            # This is still complex.

            # Simpler encoding: use the fact that equal_ik = (NOT(s[i] XOR s[(i+k)%n]))
            # And XOR in boolean algebra: a XOR b = (a | b) - (a & b)
            # But we can't compute a & b with hermax...

            # Let me use yet another approach: post constraints separately
            # equal_ik = true iff s[i] == s[(i+k)%n]
            # Equivalently:
            # - If s[i] = 0 and s[(i+k)%n] = 0, then equal_ik = true
            # - If s[i] = 0 and s[(i+k)%n] = 1, then equal_ik = false
            # - If s[i] = 1 and s[(i+k)%n] = 0, then equal_ik = false
            # - If s[i] = 1 and s[(i+k)%n] = 1, then equal_ik = true

            # This is a function we can represent as: equal_ik = NOT(s[i] != s[(i+k)%n])
            # equal_ik = NOT(XNOR(s[i], s[(i+k)%n]))
            # Wait, XNOR is the same as equality...

            # Let me just add constraints directly to the model
            # equal_ik >= s[i] + s[(i+k)%n] - 1  (if both true, equal must be true)
            # equal_ik >= (1 - s[i]) + (1 - s[(i+k)%n]) - 1 (if both false, equal must be true)
            # equal_ik <= s[i] + s[(i+k)%n]  (if different, equal must be false)
            # equal_ik <= (1 - s[i]) + (1 - s[(i+k)%n])  (if different, equal must be false)

            # Actually simpler: equal_ik = 2 * (s[i] XNOR s[(i+k)%n])
            # But encoding XNOR directly is still complex

            # Try this: equal_ik is true iff (s[i] + s[(i+k)%n]) is 0 or 2
            # Constraint: if s[i] + s[(i+k)%n] == 1, then equal_ik = false
            #             otherwise equal_ik = true (or can be true)
            # Implication: (s[i] + s[(i+k)%n] == 1) -> equal_ik == false
            # Or: equal_ik -> (s[i] + s[(i+k)%n] != 1)

            # Create constraint: if equal_ik is true, then s[i] == s[(i+k)%n]
            # If equal_ik, then s[i] + s[(i+k)%n] must be 0 or 2
            model &= ~equal_ik | (sum_ik == 0) | (sum_ik == 2)

            # And the reverse: if s[i] == s[(i+k)%n], then equal_ik must be true
            model &= (sum_ik == 1) | equal_ik

            count_expr += equal_ik

        # C_k = 2 * count_expr - n
        c_k = 2 * count_expr - n
        c_k_vars.append(c_k)

    # Objective: minimize sum of C_k^2
    # Add soft clauses for penalty
    for k_idx, c_k_expr in enumerate(c_k_vars):
        c_k_var = model.int(f"c_{k_idx + 1}", -n, n)
        model &= (c_k_var == c_k_expr)

        # Penalize squared value
        # For each possible |C_k| value, add penalty to soft clauses
        for abs_val in range(1, n + 1):
            is_abs_val = model.bool(f"c_{k_idx + 1}_abs_{abs_val}")

            # is_abs_val = true iff |c_k_var| == abs_val
            # i.e., (c_k_var == abs_val) | (c_k_var == -abs_val)
            model &= ~is_abs_val | (c_k_var == abs_val) | (c_k_var == -abs_val)
            model &= ((c_k_var != abs_val) & (c_k_var != -abs_val)) | is_abs_val

            # Add penalty: cost = abs_val^2
            cost = abs_val * abs_val
            model.obj[cost] += is_abs_val

    # Output sequence (pad to 10)
    output_seq = model.int_vector("sequence", 10, -1, 1)
    for i in range(min(n, 10)):
        model &= (output_seq[i] == 2 * s[i] - 1)
    for i in range(n, 10):
        model &= (output_seq[i] == 0)  # Pad with 0

    return model, {"sequence": output_seq}
