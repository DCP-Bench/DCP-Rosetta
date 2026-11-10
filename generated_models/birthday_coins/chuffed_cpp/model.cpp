#include "dcp.h"

// Birthday coins: Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence)
// or a sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
// worth £1 5s 6d. How many half-crowns could he have been given?
void Build(const json& instance, json& outputs) {
  (void)instance;  // no fields: every number below is from the problem statement

  // How many coins of each kind he was given: a kind may be absent (0), and no kind can
  // number more than the 15 coins.
  IntVar* half_crowns = newIntVar(0, 15);
  IntVar* shillings = newIntVar(0, 15);
  IntVar* sixpences = newIntVar(0, 15);
  vec<IntVar*> coins;
  coins.push(half_crowns);
  coins.push(shillings);
  coins.push(sixpences);

  // He was given 15 coins.
  int_linear(coins, IRT_EQ, 15);

  // They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
  // shilling 12 and a sixpence 6.
  vec<int> pence;
  pence.push(30);
  pence.push(12);
  pence.push(6);
  int_linear(pence, coins, IRT_EQ, 306);

  branch(coins, VAR_INORDER, VAL_MIN);

  outputs = {{"half_crowns", dcp::out(half_crowns)}};
}
