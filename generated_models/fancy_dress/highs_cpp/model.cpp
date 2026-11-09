#include "dcp.h"

// Fancy dress: Mr Greenguest chooses which green items to wear to Mr Greenfan's party, and
// pays the $11 entrance fee if he is not dressed according to rules 1-3, at the lowest total
// cost. He owns a green shirt; a green tie costs $10, a used green hat $2, green socks $12.
void build(const json& instance, Highs& h, dcp::Outputs& out) {
  (void)instance;  // no fields: every number below is from the problem statement

  dcp::Lin tie = dcp::new_var(h, 0, 1);    // 1 when he wears a green tie
  dcp::Lin hat = dcp::new_var(h, 0, 1);    // 1 when he wears a green hat
  dcp::Lin shirt = dcp::new_var(h, 0, 1);  // 1 when he wears a green shirt
  dcp::Lin socks = dcp::new_var(h, 0, 1);  // 1 when he wears green socks
  dcp::Lin fee = dcp::new_var(h, 0, 1);    // 1 when he pays the entrance fee

  // Rule 4: a guest who is not dressed according to rules 1-3 must pay the fee. Each rule
  // below is written as "what it asks for, or the fee": a row  item <= wanted + fee  says
  // that wearing the item needs one of the wanted items, unless he pays.

  // Rule 1: if someone wears a green tie he has to wear a green shirt.
  dcp::add_row(h, tie - shirt - fee, -kHighsInf, 0);

  // Rule 2: a guest who wears green socks or a green shirt must also wear a green tie or a
  // green hat: the socks need a tie or a hat, and so does the shirt.
  dcp::add_row(h, socks - tie - hat - fee, -kHighsInf, 0);
  dcp::add_row(h, shirt - tie - hat - fee, -kHighsInf, 0);

  // Rule 3: a guest wearing a green shirt or a green hat or who does not wear green socks
  // must wear a green tie: the shirt, the hat and bare feet (1 - socks) each need the tie.
  dcp::add_row(h, shirt - tie - fee, -kHighsInf, 0);
  dcp::add_row(h, hat - tie - fee, -kHighsInf, 0);
  dcp::add_row(h, (1 - socks) - tie - fee, -kHighsInf, 0);

  // Minimise the total cost: the tie, the hat, the socks and the fee (the shirt he owns).
  out.minimize(10 * tie + 2 * hat + 12 * socks + 11 * fee);

  out.add("t", tie);
  out.add("h", hat);
  out.add("r", shirt);
  out.add("s", socks);
  out.add("n", fee);
}
