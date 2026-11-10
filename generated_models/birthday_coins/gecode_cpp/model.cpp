#include "dcp.h"

// Birthday coins: Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence)
// or a sixpence (6 pence), though not necessarily coins of all three kinds. Together they are
// worth £1 5s 6d. How many half-crowns could he have been given?
class BirthdayCoins : public dcp::Space {
 protected:
  // How many coins of each kind he was given, in the order half-crowns, shillings,
  // sixpences: a kind may be absent (0), and no kind can number more than the 15 coins.
  IntVarArray coins;

 public:
  explicit BirthdayCoins(const json& instance) {
    (void)instance;  // no fields: every number below is from the problem statement
    coins = IntVarArray(*this, 3, 0, 15);

    // He was given 15 coins.
    linear(*this, coins, IRT_EQ, 15);

    // They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
    // shilling 12 and a sixpence 6.
    linear(*this, IntArgs({30, 12, 6}), coins, IRT_EQ, 306);

    branch(*this, coins, INT_VAR_NONE(), INT_VAL_MIN());
    output("half_crowns", coins[0]);
  }

  BirthdayCoins(BirthdayCoins& other) : dcp::Space(other) { coins.update(*this, other.coins); }
  Gecode::Space* copy() override { return new BirthdayCoins(*this); }
};

DCP_MODEL(BirthdayCoins)
