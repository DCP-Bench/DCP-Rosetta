/* Split items into two groups so that the weight difference is as small as possible,
   then list every optimal split. Optimisation is a loop with a strict bound; the optimal
   solutions are enumerated in a fresh context that fixes the objective to the optimum. */
#include <stdio.h>
#include <stdlib.h>
#include <yices.h>

#define N 6
static const int W[N] = {3, 1, 1, 2, 2, 1};

static term_t chk(term_t t) {
  if (t < 0) { yices_print_error(stderr); exit(1); }
  return t;
}
static void assert_(context_t *ctx, term_t f) {
  if (yices_assert_formula(ctx, chk(f)) < 0) { yices_print_error(stderr); exit(1); }
}

static term_t side[N];   /* side[i] in {0,1}: the group of item i */
static term_t diff;      /* |weight(group 1) - weight(group 0)| */

/* Terms are global, so any number of contexts can share them. */
static context_t *new_context(void) {
  context_t *ctx = yices_new_context(NULL);
  for (int i = 0; i < N; i++) {
    assert_(ctx, yices_arith_geq_atom(side[i], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(side[i], yices_int32(1)));
  }
  return ctx;
}

static int64_t value(model_t *mdl, term_t t) {
  int64_t v;
  if (yices_get_int64_value(mdl, t, &v) < 0) { yices_print_error(stderr); exit(1); }
  return v;
}

int main(void) {
  yices_init();
  term_t parts[N];
  int total = 0;
  for (int i = 0; i < N; i++) {
    side[i] = yices_new_uninterpreted_term(yices_int_type());
    parts[i] = yices_mul(yices_int32(2 * W[i]), side[i]);   /* 2*w*side */
    total += W[i];
  }
  diff = chk(yices_abs(yices_sub(yices_sum(N, parts), yices_int32(total))));

  /* 1. Minimise: after each model require a strictly smaller objective. */
  context_t *ctx = new_context();
  int64_t best = -1;
  smt_status_t status;
  while ((status = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    best = value(mdl, diff);
    yices_free_model(mdl);
    assert_(ctx, yices_arith_lt_atom(diff, yices_int64(best)));
  }
  yices_free_context(ctx);
  if (best < 0) { printf("No solution (status %d)\n", (int)status); return 0; }
  printf("Optimum: %lld (%s)\n", (long long)best,
         status == YICES_STATUS_UNSAT ? "proven" : "not proven");

  /* 2. Every optimal solution: fresh context, objective == optimum, no-good loop. */
  ctx = new_context();
  assert_(ctx, yices_arith_eq_atom(diff, yices_int64(best)));
  int count = 0;
  while (yices_check_context(ctx, NULL) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    term_t differs[N];
    for (int i = 0; i < N; i++) {
      int64_t v = value(mdl, side[i]);
      printf("%lld", (long long)v);
      differs[i] = yices_arith_neq_atom(side[i], yices_int64(v));
    }
    printf("\n");
    yices_free_model(mdl);
    count++;
    assert_(ctx, yices_or(N, differs));
  }
  printf("Optimal solutions: %d\n", count);
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
