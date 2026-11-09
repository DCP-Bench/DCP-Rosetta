#include "dcp.h"

// Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
// pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
// cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.

// Posts one clause: at least one literal of `pos` is true or one of `neg` is false.
// Chuffed has no Boolean expressions, so every rule is written as its clauses.
static void clause(std::initializer_list<BoolView> pos, std::initializer_list<BoolView> neg) {
  vec<BoolView> p, q;
  for (BoolView b : pos) p.push(b);
  for (BoolView b : neg) q.push(b);
  bool_clause(p, q);
}

void Build(const json& instance, json& outputs) {
  (void)instance;  // no fields: every number below is from the problem statement

  BoolView t = newBoolVar();  // he wears a green tie
  BoolView h = newBoolVar();  // he wears a green hat
  BoolView r = newBoolVar();  // he wears a green shirt
  BoolView s = newBoolVar();  // he wears green socks
  BoolView n = newBoolVar();  // he pays the entrance fee

  // Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so every
  // clause of rules 1-3 below also holds when he pays (n).

  // Rule 1: if someone wears a green tie he has to wear a green shirt.
  clause({r, n}, {t});
  // Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or a
  // green hat: socks need a tie or a hat, and so does the shirt.
  clause({t, h, n}, {s});
  clause({t, h, n}, {r});
  // Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
  // must wear a green tie: the shirt, the hat and bare feet each need the tie.
  clause({t, n}, {r});
  clause({t, n}, {h});
  clause({t, s, n}, {});

  // The choices as 0/1 integers, for the cost and the outputs.
  IntVar* ti = newIntVar(0, 1);
  IntVar* hi = newIntVar(0, 1);
  IntVar* ri = newIntVar(0, 1);
  IntVar* si = newIntVar(0, 1);
  IntVar* ni = newIntVar(0, 1);
  bool2int(t, ti);
  bool2int(h, hi);
  bool2int(r, ri);
  bool2int(s, si);
  bool2int(n, ni);

  // Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
  IntVar* cost = newIntVar(0, 10 + 2 + 12 + 11);
  vec<int> price;
  vec<IntVar*> bought;
  price.push(10); bought.push(ti);
  price.push(2);  bought.push(hi);
  price.push(12); bought.push(si);
  price.push(11); bought.push(ni);
  int_linear(price, bought, IRT_EQ, cost);
  optimize(cost, OPT_MIN);

  vec<IntVar*> choices;
  choices.push(ti); choices.push(hi); choices.push(ri); choices.push(si); choices.push(ni);
  branch(choices, VAR_INORDER, VAL_MIN);

  outputs = {{"t", dcp::out(ti)}, {"h", dcp::out(hi)}, {"r", dcp::out(ri)},
             {"s", dcp::out(si)}, {"n", dcp::out(ni)}};
}
