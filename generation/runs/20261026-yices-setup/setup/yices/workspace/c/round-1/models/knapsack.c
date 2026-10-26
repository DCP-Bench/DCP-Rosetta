/* 0/1 knapsack: maximise the total value with total weight <= capacity.
 * take[i] is a Boolean; weight and value are sums of ite(take[i], w, 0).
 * The value is maximised by tightening value > best until UNSAT.
 * Prints one optimal {"take": [...]} on stdout. */
#include <stdio.h>
#include <stdlib.h>
#include <yices.h>
#include <cjson/cJSON.h>

static char *read_file(const char *path) {
  FILE *f = fopen(path, "rb");
  if (!f) { perror(path); exit(2); }
  fseek(f, 0, SEEK_END);
  long n = ftell(f);
  fseek(f, 0, SEEK_SET);
  char *buf = malloc((size_t)n + 1);
  if (fread(buf, 1, (size_t)n, f) != (size_t)n) { perror("read"); exit(2); }
  buf[n] = '\0';
  fclose(f);
  return buf;
}

static term_t chk(term_t t) {
  if (t < 0) { yices_print_error(stderr); exit(1); }
  return t;
}

static void assert_f(context_t *ctx, term_t t) {
  chk(t);
  if (yices_assert_formula(ctx, t) < 0) { yices_print_error(stderr); exit(1); }
}

static int64_t get_int(model_t *m, term_t t) {
  int64_t v;
  if (yices_get_int64_value(m, t, &v) != 0) { yices_print_error(stderr); exit(1); }
  return v;
}

int main(int argc, char **argv) {
  if (argc != 2) { fprintf(stderr, "usage: %s INSTANCE.json\n", argv[0]); return 2; }
  cJSON *inst = cJSON_Parse(read_file(argv[1]));
  if (!inst) { fprintf(stderr, "invalid JSON\n"); return 2; }
  cJSON *weights = cJSON_GetObjectItemCaseSensitive(inst, "weights");
  cJSON *values = cJSON_GetObjectItemCaseSensitive(inst, "values");
  int64_t capacity = (int64_t)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(inst, "capacity"));
  int n = cJSON_GetArraySize(weights);

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t *take = malloc(sizeof(term_t) * (size_t)n);
  term_t *wterm = malloc(sizeof(term_t) * (size_t)n);
  term_t *vterm = malloc(sizeof(term_t) * (size_t)n);
  for (int i = 0; i < n; i++) {
    int32_t w = (int32_t)cJSON_GetNumberValue(cJSON_GetArrayItem(weights, i));
    int32_t v = (int32_t)cJSON_GetNumberValue(cJSON_GetArrayItem(values, i));
    take[i] = chk(yices_new_uninterpreted_term(yices_bool_type()));
    wterm[i] = chk(yices_ite(take[i], yices_int32(w), yices_int32(0)));
    vterm[i] = chk(yices_ite(take[i], yices_int32(v), yices_int32(0)));
  }
  term_t total_w = chk(yices_sum((uint32_t)n, wterm));
  term_t total_v = chk(yices_sum((uint32_t)n, vterm));
  assert_f(ctx, yices_arith_leq_atom(total_w, yices_int64(capacity)));

  int32_t *best_take = malloc(sizeof(int32_t) * (size_t)n);
  int found = 0;
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t val = get_int(mdl, total_v);
    for (int i = 0; i < n; i++)
      if (yices_get_bool_value(mdl, take[i], &best_take[i]) != 0) { yices_print_error(stderr); exit(1); }
    yices_free_model(mdl);
    found = 1;
    assert_f(ctx, yices_arith_gt_atom(total_v, yices_int64(val)));
  }
  if (st != YICES_STATUS_UNSAT || !found) {
    fprintf(stderr, "no optimal selection found (status %d)\n", (int)st);
    return 1;
  }
  printf("{\"take\": [");
  for (int i = 0; i < n; i++) printf("%s%d", i ? ", " : "", best_take[i] ? 1 : 0);
  printf("]}\n");
  yices_free_context(ctx);
  cJSON_Delete(inst);
  yices_exit();
  return 0;
}
