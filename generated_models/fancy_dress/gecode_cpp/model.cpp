#include "dcp.h"

// Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
// pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
// cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.
class FancyDress : public dcp::Space {
 protected:
  BoolVar t;  // he wears a green tie
  BoolVar h;  // he wears a green hat
  BoolVar r;  // he wears a green shirt
  BoolVar s;  // he wears green socks
  BoolVar n;  // he pays the entrance fee
  IntVar cost;

 public:
  explicit FancyDress(const json& instance) {
    (void)instance;  // no fields: every number below is from the problem statement
    t = BoolVar(*this, 0, 1);
    h = BoolVar(*this, 0, 1);
    r = BoolVar(*this, 0, 1);
    s = BoolVar(*this, 0, 1);
    n = BoolVar(*this, 0, 1);

    // Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee, so each
    // rule holds or he pays (`>>` is implication).
    // Rule 1: if someone wears a green tie he has to wear a green shirt.
    rel(*this, (t >> r) || n);
    // Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or
    // a green hat.
    rel(*this, ((s || r) >> (t || h)) || n);
    // Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
    // must wear a green tie.
    rel(*this, ((r || h || !s) >> t) || n);

    // Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
    cost = expr(*this, 10 * t + 2 * h + 12 * s + 11 * n);
    minimize(cost);

    BoolVarArgs choices;
    choices << t << h << r << s << n;
    branch(*this, choices, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    output("t", t);
    output("h", h);
    output("r", r);
    output("s", s);
    output("n", n);
  }

  FancyDress(FancyDress& other) : dcp::Space(other) {
    t.update(*this, other.t);
    h.update(*this, other.h);
    r.update(*this, other.r);
    s.update(*this, other.s);
    n.update(*this, other.n);
    cost.update(*this, other.cost);
  }
  Gecode::Space* copy() override { return new FancyDress(*this); }
};

DCP_MODEL(FancyDress)
