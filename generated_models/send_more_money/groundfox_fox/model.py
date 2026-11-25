# send_more_money: a FOX model for GroundFOX from DCP Rosetta.
#
# The "Send More Money" puzzle is a classic cryptarithmetic problem where each letter
# represents a unique digit. The goal is to assign digits to the letters such that the
# following equation holds true:
#
# ```text SEND + MORE ------ MONEY ```
#
# Each letter must be assigned a unique digit from 0 to 9, and the first letter of each word
# cannot be zero.
#
# Print the values assigned to each letter (s, e, n, d, m, o, r, y).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py send_more_money.json --check

# send_more_money: a FOX model for GroundFOX from DCP Rosetta.
#
#    SEND
#  + MORE
#  ------
#   MONEY
#
# Each letter is a digit 0..9, all letters distinct, leading letters non-zero.
# Carries k1 (units to tens), k2 (tens to hundreds), k3 (hundreds to thousands)
# are 0/1 bits. Every column forbids the digit/carry tuples that are not allowed
# by its addition; the allowed tuples are data relations computed in structure().

_LETTERS = ["d", "e", "m", "n", "o", "r", "s", "y"]


def _build_fox():
    inv = "invocabulary { Dig/1 Bit/1 Add/5 Add0/4 Add4/4 }"
    out = "outvocabulary { " + " ".join(f"{x}/1" for x in _LETTERS) + " k1/1 k2/1 k3/1 }"
    body = []
    for x in _LETTERS:
        body.append(f"? v [Dig(v)] : {x}(v).")
        body.append(f"! v [Dig(v)] : ! w [Dig(w) & v ~= w] : ~{x}(v) | ~{x}(w).")
    for i, x in enumerate(_LETTERS):
        for y in _LETTERS[i + 1:]:
            body.append(f"! v [Dig(v)] : ~{x}(v) | ~{y}(v).")
    body.append("! u [u = 0] : ~s(0).")
    body.append("! u [u = 0] : ~m(0).")
    for k in ["k1", "k2", "k3"]:
        body.append(f"! u [u = 0] : {k}(0) | {k}(1).")
        body.append(f"! u [u = 0] : ~{k}(0) | ~{k}(1).")
    # units: d + e = y + 10*k1
    body.append("! a [Dig(a)] : ! b [Dig(b)] : ! t [Dig(t)] : ! c [Bit(c) & ~Add0(a, b, t, c)] : "
                "~d(a) | ~e(b) | ~y(t) | ~k1(c).")
    # tens: n + r + k1 = e + 10*k2
    body.append("! a [Dig(a)] : ! b [Dig(b)] : ! ci [Bit(ci)] : ! t [Dig(t)] : "
                "! co [Bit(co) & ~Add(a, b, ci, t, co)] : ~n(a) | ~r(b) | ~k1(ci) | ~e(t) | ~k2(co).")
    # hundreds: e + o + k2 = n + 10*k3
    body.append("! a [Dig(a)] : ! b [Dig(b)] : ! ci [Bit(ci)] : ! t [Dig(t)] : "
                "! co [Bit(co) & ~Add(a, b, ci, t, co)] : ~e(a) | ~o(b) | ~k2(ci) | ~n(t) | ~k3(co).")
    # thousands: s + m + k3 = o + 10*m (the carry out is the digit m itself)
    body.append("! a [Dig(a)] : ! b [Dig(b)] : ! ci [Bit(ci)] : ! t [Dig(t) & ~Add4(a, b, ci, t)] : "
                "~s(a) | ~m(b) | ~k3(ci) | ~o(t).")
    th = "theory {\n" + "\n".join("    " + line for line in body) + "\n}\n"
    return inv + "\n" + out + "\n" + th


FOX = _build_fox()


def structure(instance):
    dig = list(range(10))
    bit = [0, 1]
    add = [(a, b, c, (a + b + c) % 10, (a + b + c) // 10)
           for a in dig for b in dig for c in bit]
    add0 = [(a, b, (a + b) % 10, (a + b) // 10) for a in dig for b in dig]
    add4 = [(a, b, c, t) for a in dig for b in dig for c in bit
            for t in dig if a + b + c == t + 10 * b]
    return {"domain": dig, "Dig": dig, "Bit": bit,
            "Add": add, "Add0": add0, "Add4": add4}
