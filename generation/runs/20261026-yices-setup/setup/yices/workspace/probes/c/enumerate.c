#include <stdio.h>
#include <yices.h>
/* all (x,y) in 1..3 with x<y, via no-goods over outputs */
int main(void) {
  yices_init();
  type_t ity = yices_int_type();
  term_t v[2]; for (int i=0;i<2;i++) v[i]=yices_new_uninterpreted_term(ity);
  context_t *ctx = yices_new_context(NULL);
  for (int i=0;i<2;i++){ yices_assert_formula(ctx, yices_arith_geq_atom(v[i], yices_int32(1))); yices_assert_formula(ctx, yices_arith_leq_atom(v[i], yices_int32(3))); }
  yices_assert_formula(ctx, yices_arith_lt_atom(v[0], v[1]));
  int n = 0; smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *m = yices_get_model(ctx, 1); int64_t val[2]; term_t ng[2];
    for (int i=0;i<2;i++){ yices_get_int64_value(m, v[i], &val[i]); ng[i]=yices_arith_neq_atom(v[i], yices_int64(val[i])); }
    printf("sol %lld %lld\n", (long long)val[0], (long long)val[1]); n++;
    yices_free_model(m);
    if (yices_assert_formula(ctx, yices_or(2, ng)) < 0) { yices_print_error(stderr); return 1; }
  }
  printf("count=%d last=%d (UNSAT=%d)\n", n, st, YICES_STATUS_UNSAT);
  yices_free_context(ctx); yices_exit(); return 0;
}
