/* 0/1 knapsack read from a JSON file (first argument, default data.json), maximise value.
   JSON is read with cJSON; all sizes come from the data. */
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
  rewind(f);
  char *buf = malloc(n + 1);
  if (fread(buf, 1, n, f) != (size_t)n) exit(1);
  buf[n] = 0;
  fclose(f);
  return buf;
}

int main(int argc, char **argv) {
  char *text = read_file(argc > 1 ? argv[1] : "data.json");
  cJSON *data = cJSON_Parse(text);
  if (!data) { fprintf(stderr, "invalid JSON\n"); return 1; }
  int capacity = cJSON_GetObjectItemCaseSensitive(data, "capacity")->valueint;
  cJSON *items = cJSON_GetObjectItemCaseSensitive(data, "items");
  int n = cJSON_GetArraySize(items);              /* size comes from the data */

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t *take = malloc(n * sizeof(term_t)), *w = malloc(n * sizeof(term_t)), *v = malloc(n * sizeof(term_t));
  for (int i = 0; i < n; i++) {
    cJSON *it = cJSON_GetArrayItem(items, i);
    int weight = cJSON_GetObjectItemCaseSensitive(it, "weight")->valueint;
    int value = cJSON_GetObjectItemCaseSensitive(it, "value")->valueint;
    take[i] = yices_new_uninterpreted_term(yices_int_type());
    assert_(ctx, yices_arith_geq_atom(take[i], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(take[i], yices_int32(1)));
    w[i] = yices_mul(yices_int32(weight), take[i]);
    v[i] = yices_mul(yices_int32(value), take[i]);
  }
  assert_(ctx, yices_arith_leq_atom(yices_sum(n, w), yices_int32(capacity)));
  /* ragged list: conflicts[i] holds any number of items that cannot be taken together with item i */
  cJSON *conflicts = cJSON_GetObjectItemCaseSensitive(data, "conflicts");
  for (int i = 0; i < cJSON_GetArraySize(conflicts); i++) {
    cJSON *row = cJSON_GetArrayItem(conflicts, i);
    for (int k = 0; k < cJSON_GetArraySize(row); k++) {
      int j = cJSON_GetArrayItem(row, k)->valueint;
      term_t both[2] = { yices_arith_gt_atom(take[i], yices_int32(0)), yices_arith_gt_atom(take[j], yices_int32(0)) };
      assert_(ctx, yices_not(yices_and(2, both)));
    }
  }
  term_t objective = chk(yices_sum(n, v));

  /* Maximise: after each model require a strictly larger objective. */
  int64_t best = -1;
  int64_t *chosen = calloc(n, sizeof(int64_t));
  smt_status_t status;
  while ((status = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    yices_get_int64_value(mdl, objective, &best);
    for (int i = 0; i < n; i++) yices_get_int64_value(mdl, take[i], &chosen[i]);
    yices_free_model(mdl);
    assert_(ctx, yices_arith_gt_atom(objective, yices_int64(best)));
  }
  if (best < 0) { printf("No solution (status %d)\n", (int)status); return 0; }
  printf("Objective: %lld (%s)\n", (long long)best, status == YICES_STATUS_UNSAT ? "optimal" : "best found, not proven");
  for (int i = 0; i < n; i++)
    if (chosen[i]) printf("take %s\n", cJSON_GetObjectItemCaseSensitive(cJSON_GetArrayItem(items, i), "name")->valuestring);
  yices_free_context(ctx);
  yices_exit();
  cJSON_Delete(data);
  free(text);
  return 0;
}
