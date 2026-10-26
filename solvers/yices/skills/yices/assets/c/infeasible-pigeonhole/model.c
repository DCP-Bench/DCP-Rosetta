/* Five pigeons, four holes, every pigeon in its own hole: infeasible.
   UNSAT is a normal return value, not an error. */
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

int main(void) {
  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t hole[5];
  for (int i = 0; i < 5; i++) {
    hole[i] = yices_new_uninterpreted_term(yices_int_type());
    assert_(ctx, yices_arith_geq_atom(hole[i], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(hole[i], yices_int32(3)));
  }
  assert_(ctx, yices_distinct(5, hole));

  smt_status_t status = yices_check_context(ctx, NULL);
  switch (status) {
    case YICES_STATUS_SAT:   printf("Status: sat\n"); break;
    case YICES_STATUS_UNSAT: printf("Status: unsat (proven infeasible)\n"); break;
    default:                 printf("Status: %d (unknown or interrupted)\n", (int)status);
  }
  /* There is no model after UNSAT: yices_get_model returns NULL with error CTX_INVALID_OPERATION. */
  model_t *mdl = yices_get_model(ctx, 1);
  printf("Model after unsat: %s\n", mdl ? "yes" : "none");
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
