#include <stdio.h>
#include <yices.h>

int main(void) {
  yices_init();                                   /* first call of any program */
  term_t x = yices_new_uninterpreted_term(yices_int_type());   /* a decision variable */
  term_t y = yices_new_uninterpreted_term(yices_int_type());
  context_t *ctx = yices_new_context(NULL);       /* NULL: default configuration */
  yices_assert_formula(ctx, yices_arith_geq_atom(x, yices_int32(1)));
  yices_assert_formula(ctx, yices_arith_leq_atom(x, yices_int32(5)));
  yices_assert_formula(ctx, yices_arith_eq_atom(yices_add(x, y), yices_int32(7)));
  yices_assert_formula(ctx, yices_arith_gt_atom(x, y));

  if (yices_check_context(ctx, NULL) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);       /* keep_subst = 1 */
    int64_t vx, vy;
    if (yices_get_int64_value(mdl, x, &vx) == 0 && yices_get_int64_value(mdl, y, &vy) == 0)
      printf("x=%lld y=%lld\n", (long long)vx, (long long)vy);
    yices_free_model(mdl);
  }
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
