/* Factor 91 = x * y with 1 < x < y. A product of two variables is rejected by the default
   context; a context configured for QF_NIA uses the MCSAT solver. */
#include <stdio.h>
#include <stdlib.h>
#include <yices.h>

static term_t chk(term_t t) {
  if (t < 0) { yices_print_error(stderr); exit(1); }
  return t;
}

static void bounds(context_t *ctx, term_t t, int lo, int hi) {
  yices_assert_formula(ctx, yices_arith_geq_atom(t, yices_int32(lo)));
  yices_assert_formula(ctx, yices_arith_leq_atom(t, yices_int32(hi)));
}

int main(void) {
  yices_init();
  term_t x = yices_new_uninterpreted_term(yices_int_type());
  term_t y = yices_new_uninterpreted_term(yices_int_type());
  term_t product = chk(yices_mul(x, y));                 /* building the term works */
  term_t eq = chk(yices_arith_eq_atom(product, yices_int32(91)));

  context_t *plain = yices_new_context(NULL);
  if (yices_assert_formula(plain, eq) < 0) {
    char *msg = yices_error_string();
    printf("Default context: %s\n", msg);
    yices_free_string(msg);
    yices_clear_error();
  }
  yices_free_context(plain);

  printf("MCSAT available: %s\n", yices_has_mcsat() ? "yes" : "no");
  ctx_config_t *cfg = yices_new_config();
  if (yices_default_config_for_logic(cfg, "QF_NIA") < 0) { yices_print_error(stderr); return 1; }
  context_t *ctx = yices_new_context(cfg);
  yices_free_config(cfg);
  bounds(ctx, x, 2, 91);
  bounds(ctx, y, 2, 91);
  yices_assert_formula(ctx, chk(yices_arith_eq_atom(product, yices_int32(91))));
  yices_assert_formula(ctx, chk(yices_arith_lt_atom(x, y)));

  smt_status_t status = yices_check_context(ctx, NULL);
  if (status == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t vx, vy;
    if (yices_get_int64_value(mdl, x, &vx) < 0 || yices_get_int64_value(mdl, y, &vy) < 0) return 1;
    yices_free_model(mdl);
    printf("x=%lld y=%lld\n", (long long)vx, (long long)vy);
  } else {
    printf("Status: %d\n", (int)status);
  }
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
