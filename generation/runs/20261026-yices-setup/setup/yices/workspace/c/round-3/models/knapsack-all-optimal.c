/* All optimal 0/1 knapsack selections. Phase 1 finds the optimum by tightening.
   Phase 2 builds a fresh context with value == optimum and enumerates every
   selection with a no-good over the x[i] only. */
#include <stdio.h>
#include <stdlib.h>
#include <cjson/cJSON.h>
#include <yices.h>

static term_t chk(term_t t) {
  if (t < 0) { yices_print_error(stderr); exit(1); }
  return t;
}
static void assert_(context_t *ctx, term_t f) {
  if (yices_assert_formula(ctx, chk(f)) < 0) { yices_print_error(stderr); exit(1); }
}

static char *read_file(const char *path) {
  FILE *f = fopen(path, "rb");
  if (!f) { perror(path); exit(1); }
  fseek(f, 0, SEEK_END);
  long n = ftell(f);
  fseek(f, 0, SEEK_SET);
  char *buf = malloc((size_t)n + 1);
  if (fread(buf, 1, (size_t)n, f) != (size_t)n) { perror("read"); exit(1); }
  buf[n] = '\0';
  fclose(f);
  return buf;
}

static int n, W[64], V[64], cap;
static term_t x[64], obj;

/* Capacity constraint, shared by both phases (terms are global, so reuse them). */
static void assert_model(context_t *ctx) {
  term_t wterms[64];
  for (int i = 0; i < n; i++) {
    assert_(ctx, yices_arith_geq_atom(x[i], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(x[i], yices_int32(1)));
    wterms[i] = chk(yices_mul(yices_int32(W[i]), x[i]));
  }
  assert_(ctx, yices_arith_leq_atom(chk(yices_sum(n, wterms)), yices_int32(cap)));
}

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 1; }
  char *text = read_file(argv[1]);
  cJSON *root = cJSON_Parse(text);
  if (!root) { fprintf(stderr, "invalid JSON\n"); return 1; }
  cJSON *wj = cJSON_GetObjectItemCaseSensitive(root, "weights");
  cJSON *vj = cJSON_GetObjectItemCaseSensitive(root, "values");
  n = cJSON_GetArraySize(wj);
  cap = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "capacity"));
  for (int i = 0; i < n; i++) {
    W[i] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(wj, i));
    V[i] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(vj, i));
  }

  yices_init();

  /* Decision variables and objective, created once. */
  term_t vterms[64];
  for (int i = 0; i < n; i++) {
    x[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    vterms[i] = chk(yices_mul(yices_int32(V[i]), x[i]));
  }
  obj = chk(yices_sum(n, vterms));

  /* Phase 1: optimum by tightening. */
  int64_t best = 0;
  int have = 0;
  context_t *ctx = yices_new_context(NULL);
  assert_model(ctx);
  while (yices_check_context(ctx, NULL) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t ov;
    if (yices_get_int64_value(mdl, obj, &ov) < 0) { yices_print_error(stderr); return 1; }
    yices_free_model(mdl);
    best = ov;
    have = 1;
    assert_(ctx, yices_arith_gt_atom(obj, yices_int32((int32_t)best)));
  }
  yices_free_context(ctx);

  if (!have) {
    printf("{\"status\": \"unsatisfiable\"}\n");
    cJSON_Delete(root);
    free(text);
    yices_exit();
    return 0;
  }

  /* Phase 2: every selection with value == optimum, enumerated by no-goods. */
  ctx = yices_new_context(NULL);
  assert_model(ctx);
  assert_(ctx, yices_arith_eq_atom(obj, yices_int32((int32_t)best)));

  term_t differs[64];
  while (yices_check_context(ctx, NULL) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int take[64];
    for (int i = 0; i < n; i++) {
      int64_t t;
      if (yices_get_int64_value(mdl, x[i], &t) < 0) { yices_print_error(stderr); return 1; }
      take[i] = (int)t;
    }
    yices_free_model(mdl);

    printf("{\"take\": [");
    for (int i = 0; i < n; i++) {
      printf("%s%d", i ? ", " : "", take[i]);
      differs[i] = yices_arith_neq_atom(x[i], yices_int32(take[i]));
    }
    printf("]}\n");

    assert_(ctx, yices_or(n, differs));
  }

  yices_free_context(ctx);
  cJSON_Delete(root);
  free(text);
  yices_exit();
  return 0;
}
