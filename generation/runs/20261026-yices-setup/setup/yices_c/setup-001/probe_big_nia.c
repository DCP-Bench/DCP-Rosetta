#include "dcp.h"
void build(const cJSON *instance) {
  dcp_set_logic("QF_NIA");
  term_t x = yices_new_uninterpreted_term(yices_int_type());
  term_t y = yices_new_uninterpreted_term(yices_int_type());
  dcp_assert(yices_arith_geq_atom(x, yices_int32(1)));
  dcp_assert(yices_arith_leq_atom(x, yices_int32(10)));
  dcp_assert(yices_arith_geq_atom(y, yices_int32(1)));
  dcp_assert(yices_arith_leq_atom(y, yices_int32(10)));
  dcp_assert(yices_arith_geq_atom(yices_mul(x, y), yices_int32(12)));
  dcp_maximize(yices_sub(yices_mul(yices_int32(7), x), yices_mul(x, y)));
  term_t big = yices_parse_term("1000000000000000000000000000000");
  dcp_output("x", dcp_term(x)); dcp_output("y", dcp_term(y)); dcp_output("big", dcp_term(big));
}
