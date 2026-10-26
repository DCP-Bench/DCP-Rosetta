/* All solutions of 5-queens: queen i is in row i, q[i] is its column.
   After each model a no-good over the output terms excludes that assignment. */
#include <stdio.h>
#include <stdlib.h>
#include <yices.h>

static term_t chk(term_t t) {
  if (t < 0) { yices_print_error(stderr); exit(1); }
  return t;
}
static void assert_(context_t *ctx, term_t f) {
  if (yices_assert_formula(ctx, chk(f)) < 0) { yices_print_error(stderr); exit(1); }
}

#define N 5

int main(void) {
  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t q[N];
  for (int i = 0; i < N; i++) {
    q[i] = yices_new_uninterpreted_term(yices_int_type());
    assert_(ctx, yices_arith_geq_atom(q[i], yices_int32(0)));
    assert_(ctx, yices_arith_lt_atom(q[i], yices_int32(N)));
  }
  assert_(ctx, yices_distinct(N, q));                        /* columns */
  for (int i = 0; i < N; i++)
    for (int j = i + 1; j < N; j++) {                        /* diagonals */
      assert_(ctx, yices_arith_neq_atom(yices_sub(q[i], q[j]), yices_int32(j - i)));
      assert_(ctx, yices_arith_neq_atom(yices_sub(q[j], q[i]), yices_int32(j - i)));
    }

  int count = 0;
  smt_status_t status;
  while ((status = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    term_t differs[N];
    printf("solution:");
    for (int i = 0; i < N; i++) {
      int64_t v;
      if (yices_get_int64_value(mdl, q[i], &v) < 0) { yices_print_error(stderr); return 1; }
      printf(" %lld", (long long)v);
      differs[i] = yices_arith_neq_atom(q[i], yices_int64(v));
    }
    printf("\n");
    yices_free_model(mdl);
    count++;
    /* No-good over the outputs. Do not use yices_assert_blocking_clause: it blocks the
       Boolean atom assignment, not the integer values. */
    assert_(ctx, yices_or(N, differs));
  }
  printf("Solutions: %d\n", count);
  printf("Last status: %s\n", status == YICES_STATUS_UNSAT ? "UNSAT (complete)" : "not complete");
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
