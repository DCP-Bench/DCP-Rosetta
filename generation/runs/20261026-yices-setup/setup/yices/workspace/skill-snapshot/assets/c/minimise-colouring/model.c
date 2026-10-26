/* Colour a wheel graph (hub 0, rim 1..5) with as few colours as possible. */
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

#define V 6
#define E 10
static const int EDGES[E][2] = {{0,1},{0,2},{0,3},{0,4},{0,5},{1,2},{2,3},{3,4},{4,5},{5,1}};

int main(void) {
  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t col[V];
  for (int v = 0; v < V; v++) {
    col[v] = yices_new_uninterpreted_term(yices_int_type());
    assert_(ctx, yices_arith_geq_atom(col[v], yices_int32(0)));
    assert_(ctx, yices_arith_lt_atom(col[v], yices_int32(V)));    /* at most V colours */
  }
  for (int e = 0; e < E; e++)
    assert_(ctx, yices_arith_neq_atom(col[EDGES[e][0]], col[EDGES[e][1]]));

  /* used[c] = 1 if some vertex has colour c; the objective counts used colours. */
  term_t used[V];
  for (int c = 0; c < V; c++) {
    term_t is_c[V];
    for (int v = 0; v < V; v++) is_c[v] = yices_arith_eq_atom(col[v], yices_int32(c));
    used[c] = chk(yices_ite(yices_or(V, is_c), yices_int32(1), yices_int32(0)));
  }
  term_t objective = chk(yices_sum(V, used));

  int64_t best = -1;
  smt_status_t status;
  while ((status = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    yices_get_int64_value(mdl, objective, &best);
    printf("found a colouring with %lld colours\n", (long long)best);
    yices_free_model(mdl);
    assert_(ctx, yices_arith_lt_atom(objective, yices_int64(best)));
  }
  printf("Colours: %lld (%s)\n", (long long)best, status == YICES_STATUS_UNSAT ? "optimal" : "not proven");
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
