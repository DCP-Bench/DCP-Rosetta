#include <stdio.h>
#include <yices.h>
int main(void) {
  yices_init();
  type_t ity = yices_int_type();
  term_t x = yices_new_uninterpreted_term(ity), y = yices_new_uninterpreted_term(ity);
  yices_set_term_name(x, "x"); yices_set_term_name(y, "y");
  context_t *ctx = yices_new_context(NULL);
  term_t c1[] = { yices_arith_geq_atom(x, yices_int32(1)), yices_arith_leq_atom(x, yices_int32(5)),
                  yices_arith_geq_atom(y, yices_int32(1)), yices_arith_leq_atom(y, yices_int32(5)),
                  yices_arith_eq_atom(yices_add(x, y), yices_int32(7)), yices_arith_gt_atom(x, y) };
  for (int i = 0; i < 6; i++) if (yices_assert_formula(ctx, c1[i]) < 0) { yices_print_error(stderr); return 1; }
  smt_status_t st = yices_check_context(ctx, NULL);
  printf("status=%d (SAT=%d)\n", st, YICES_STATUS_SAT);
  if (st == YICES_STATUS_SAT) {
    model_t *m = yices_get_model(ctx, 1);
    int64_t vx, vy;
    printf("rcx=%d rcy=%d\n", yices_get_int64_value(m, x, &vx), yices_get_int64_value(m, y, &vy));
    printf("x=%lld y=%lld\n", (long long)vx, (long long)vy);
    yices_free_model(m);
  }
  yices_free_context(ctx); yices_exit(); return 0;
}
