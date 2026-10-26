/* 0/1 knapsack: take items within the capacity with maximum total value.
   Optimised by tightening the value bound. Usage: knapsack instance.json */
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

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 2; }
  cJSON *root = cJSON_Parse(slurp(argv[1]));
  if (!root) { fprintf(stderr, "bad JSON\n"); return 1; }
  cJSON *wa = cJSON_GetObjectItemCaseSensitive(root, "weights");
  cJSON *va = cJSON_GetObjectItemCaseSensitive(root, "values");
  int64_t cap = (int64_t)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "capacity"));
  int n = cJSON_GetArraySize(wa);

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t x[n], wsum[n], vsum[n];
  for (int i = 0; i < n; i++) {
    int64_t w = (int64_t)cJSON_GetNumberValue(cJSON_GetArrayItem(wa, i));
    int64_t v = (int64_t)cJSON_GetNumberValue(cJSON_GetArrayItem(va, i));
    x[i] = chk(yices_new_uninterpreted_term(yices_bool_type()));   /* item i taken */
    wsum[i] = chk(yices_ite(x[i], chk(yices_int64(w)), chk(yices_int64(0))));
    vsum[i] = chk(yices_ite(x[i], chk(yices_int64(v)), chk(yices_int64(0))));
  }
  /* capacity */
  put(ctx, yices_arith_leq_atom(chk(yices_sum(n, wsum)), chk(yices_int64(cap))));
  term_t value = chk(yices_sum(n, vsum));

  /* tighten: each model must beat the last value; the last model is optimal */
  int64_t best = -1;
  int32_t take[n];
  for (int i = 0; i < n; i++) take[i] = 0;
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t val = 0;
    yices_get_int64_value(mdl, value, &val);
    for (int i = 0; i < n; i++) yices_get_bool_value(mdl, x[i], &take[i]);
    yices_free_model(mdl);
    best = val;
    put(ctx, yices_arith_gt_atom(value, chk(yices_int64(best))));
  }
  if (st != YICES_STATUS_UNSAT) { fprintf(stderr, "solver status %d\n", (int)st); return 1; }

  printf("{\"take\": [");
  for (int i = 0; i < n; i++) printf("%s%d", i ? ", " : "", take[i] ? 1 : 0);
  printf("]}\n");

  yices_free_context(ctx);
  yices_exit();
  cJSON_Delete(root);
  return 0;
}
