/* All optimal 0/1 knapsack selections: first find the optimal value by
   tightening, then enumerate every selection with that value in a new context
   using a no-good over the item variables. Usage: knapsack-all-optimal instance.json */
#include <stdio.h>
#include <stdlib.h>
#include <cjson/cJSON.h>
#include <yices.h>

static char *slurp(const char *path) {
  FILE *f = fopen(path, "rb");
  if (!f) { perror(path); exit(1); }
  fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
  char *buf = malloc((size_t)n + 1);
  if (fread(buf, 1, (size_t)n, f) != (size_t)n) { perror("read"); exit(1); }
  buf[n] = '\0'; fclose(f);
  return buf;
}
static term_t chk(term_t t) { if (t < 0) { yices_print_error(stderr); exit(1); } return t; }
static void put(context_t *ctx, term_t t) {
  if (yices_assert_formula(ctx, t) < 0) { yices_print_error(stderr); exit(1); }
}

static int n;
static int64_t cap;
static term_t x[64], wsum, value;

/* new context with the capacity constraint; terms are global, so they are reused */
static context_t *base_context(void) {
  context_t *ctx = yices_new_context(NULL);
  put(ctx, yices_arith_leq_atom(wsum, chk(yices_int64(cap))));
  return ctx;
}

static int64_t optimal_value(void) {
  context_t *ctx = base_context();
  int64_t best = -1;
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    yices_get_int64_value(mdl, value, &best);
    yices_free_model(mdl);
    put(ctx, yices_arith_gt_atom(value, chk(yices_int64(best))));
  }
  yices_free_context(ctx);
  return best;
}

static void enumerate_optimal(int64_t best) {
  context_t *ctx = base_context();
  put(ctx, yices_arith_eq_atom(value, chk(yices_int64(best))));
  term_t differs[64];
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    printf("{\"take\": [");
    for (int i = 0; i < n; i++) {
      int32_t b = 0;
      yices_get_bool_value(mdl, x[i], &b);
      printf("%s%d", i ? ", " : "", b ? 1 : 0);
      /* differ from this selection on at least one item */
      differs[i] = b ? chk(yices_not(x[i])) : x[i];
    }
    printf("]}\n");
    yices_free_model(mdl);
    put(ctx, chk(yices_or(n, differs)));
  }
  if (st != YICES_STATUS_UNSAT) { fprintf(stderr, "solver status %d\n", (int)st); exit(1); }
  yices_free_context(ctx);
}

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 2; }
  cJSON *root = cJSON_Parse(slurp(argv[1]));
  if (!root) { fprintf(stderr, "bad JSON\n"); return 1; }
  cJSON *wa = cJSON_GetObjectItemCaseSensitive(root, "weights");
  cJSON *va = cJSON_GetObjectItemCaseSensitive(root, "values");
  cap = (int64_t)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "capacity"));
  n = cJSON_GetArraySize(wa);

  yices_init();
  term_t wterms[64], vterms[64];
  for (int i = 0; i < n; i++) {
    int64_t w = (int64_t)cJSON_GetNumberValue(cJSON_GetArrayItem(wa, i));
    int64_t v = (int64_t)cJSON_GetNumberValue(cJSON_GetArrayItem(va, i));
    x[i] = chk(yices_new_uninterpreted_term(yices_bool_type()));
    wterms[i] = chk(yices_ite(x[i], chk(yices_int64(w)), chk(yices_int64(0))));
    vterms[i] = chk(yices_ite(x[i], chk(yices_int64(v)), chk(yices_int64(0))));
  }
  wsum = chk(yices_sum(n, wterms));
  value = chk(yices_sum(n, vterms));

  int64_t best = optimal_value();
  enumerate_optimal(best);

  yices_exit();
  cJSON_Delete(root);
  return 0;
}
