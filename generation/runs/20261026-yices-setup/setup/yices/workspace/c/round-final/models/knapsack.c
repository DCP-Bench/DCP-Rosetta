/* 0/1 knapsack: maximise the total value of the taken items within the capacity.
   Optimum is found by tightening: each SAT model asserts value > best. */
#include <stdio.h>
#include <stdlib.h>
#include <cjson/cJSON.h>
#include <yices.h>

static void assert_ok(context_t *ctx, term_t t) {
  if (yices_assert_formula(ctx, t) < 0) { yices_print_error(stderr); exit(1); }
}

static term_t chk(term_t t) {
  if (t < 0) { yices_print_error(stderr); exit(1); }
  return t;
}

static cJSON *load(const char *path) {
  FILE *f = fopen(path, "rb");
  if (!f) { perror(path); exit(1); }
  fseek(f, 0, SEEK_END);
  long len = ftell(f);
  fseek(f, 0, SEEK_SET);
  char *buf = malloc(len + 1);
  fread(buf, 1, len, f);
  buf[len] = '\0';
  fclose(f);
  cJSON *j = cJSON_Parse(buf);
  free(buf);
  if (!j) { fprintf(stderr, "invalid JSON in %s\n", path); exit(1); }
  return j;
}

static int geti(const cJSON *o, const char *key) {
  return (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(o, key));
}

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 2; }
  cJSON *inst = load(argv[1]);
  cJSON *wj = cJSON_GetObjectItemCaseSensitive(inst, "weights");
  cJSON *vj = cJSON_GetObjectItemCaseSensitive(inst, "values");
  int cap = geti(inst, "capacity");
  int n = cJSON_GetArraySize(wj);
  int *w = malloc(n * sizeof *w), *v = malloc(n * sizeof *v);
  for (int i = 0; i < n; i++) {
    w[i] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(wj, i));
    v[i] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(vj, i));
  }
  cJSON_Delete(inst);

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  /* take[i] is true when item i is taken */
  term_t *take = malloc(n * sizeof *take);
  term_t *wterm = malloc(n * sizeof *wterm), *vterm = malloc(n * sizeof *vterm);
  for (int i = 0; i < n; i++) {
    take[i] = chk(yices_new_uninterpreted_term(yices_bool_type()));
    wterm[i] = chk(yices_ite(take[i], yices_int32(w[i]), yices_int32(0)));
    vterm[i] = chk(yices_ite(take[i], yices_int32(v[i]), yices_int32(0)));
  }
  term_t weight = chk(yices_sum(n, wterm));
  term_t value = chk(yices_sum(n, vterm));
  assert_ok(ctx, yices_arith_leq_atom(weight, yices_int32(cap)));

  int64_t best = -1;
  int found = 0;
  int *best_take = malloc(n * sizeof *best_take);
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t val = 0;
    yices_get_int64_value(mdl, value, &val);
    for (int i = 0; i < n; i++) {
      int32_t b = 0;
      yices_get_bool_value(mdl, take[i], &b);
      best_take[i] = b;
    }
    yices_free_model(mdl);
    best = val;
    found = 1;
    assert_ok(ctx, yices_arith_gt_atom(value, yices_int64(best)));
  }
  if (st != YICES_STATUS_UNSAT) {
    fprintf(stderr, "solver status %d\n", (int)st);
    return 1;
  }

  if (!found) {
    printf("{\"status\": \"unsatisfiable\"}\n");
  } else {
    printf("{\"take\": [");
    for (int i = 0; i < n; i++) printf("%s%d", i ? ", " : "", best_take[i]);
    printf("]}\n");
  }

  yices_free_context(ctx);
  yices_exit();
  return 0;
}
