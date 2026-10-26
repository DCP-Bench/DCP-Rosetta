#include "dcp.h"

/* Pilot fixture for yices_c: x + y == n, or x + y >= n minimised when optimize is set. */
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  int optimize = cJSON_IsTrue(dcp_get(instance, "optimize"));
  term_t x = yices_new_uninterpreted_term(yices_int_type());
  term_t y = yices_new_uninterpreted_term(yices_int_type());
  term_t sum = dcp_chk(yices_add(x, y));
  dcp_assert(yices_arith_geq_atom(x, yices_int32(0)));
  dcp_assert(yices_arith_leq_atom(x, yices_int32(n)));
  dcp_assert(yices_arith_geq_atom(y, yices_int32(0)));
  dcp_assert(yices_arith_leq_atom(y, yices_int32(n)));
  if (optimize) {
    dcp_assert(yices_arith_geq_atom(sum, yices_int32(n)));
    dcp_minimize(sum);
  } else {
    dcp_assert(yices_arith_eq_atom(sum, yices_int32(n)));
  }
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
}
