/* 3x3 magic square: the numbers 1..9, every row, column and diagonal sums to 15. */
#include <stdio.h>
#include <stdlib.h>
#include <yices.h>

/* Builders return NULL_TERM (-1) on error and later calls cascade: check every term. */
static term_t chk(term_t t) {
  if (t < 0) { yices_print_error(stderr); exit(1); }
  return t;
}
static void assert_(context_t *ctx, term_t f) {
  if (yices_assert_formula(ctx, chk(f)) < 0) { yices_print_error(stderr); exit(1); }
}

int main(void) {
  yices_init();
  context_t *ctx = yices_new_context(NULL);

  /* Decision variables are uninterpreted terms of type int (not yices_new_variable). */
  term_t cell[9];
  for (int i = 0; i < 9; i++) {
    cell[i] = yices_new_uninterpreted_term(yices_int_type());
    assert_(ctx, yices_arith_geq_atom(cell[i], yices_int32(1)));
    assert_(ctx, yices_arith_leq_atom(cell[i], yices_int32(9)));
  }
  /* Every number is used once. */
  assert_(ctx, yices_distinct(9, cell));

  /* Every row, column and diagonal sums to 15. */
  int lines[8][3] = {{0,1,2},{3,4,5},{6,7,8},{0,3,6},{1,4,7},{2,5,8},{0,4,8},{2,4,6}};
  for (int l = 0; l < 8; l++) {
    term_t t[3];
    for (int k = 0; k < 3; k++) t[k] = cell[lines[l][k]];
    assert_(ctx, yices_arith_eq_atom(yices_sum(3, t), yices_int32(15)));
  }

  smt_status_t status = yices_check_context(ctx, NULL);
  if (status == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t v[9];
    for (int i = 0; i < 9; i++)
      if (yices_get_int64_value(mdl, cell[i], &v[i]) < 0) { yices_print_error(stderr); return 1; }
    yices_free_model(mdl);
    for (int r = 0; r < 3; r++) printf("%lld %lld %lld\n", (long long)v[3*r], (long long)v[3*r+1], (long long)v[3*r+2]);
    int ok = 1;
    for (int l = 0; l < 8; l++) ok &= (v[lines[l][0]] + v[lines[l][1]] + v[lines[l][2]] == 15);
    printf("Status: sat\nAll lines sum to 15: %s\n", ok ? "yes" : "no");
  } else {
    printf("Status: %d\n", (int)status);
  }
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
