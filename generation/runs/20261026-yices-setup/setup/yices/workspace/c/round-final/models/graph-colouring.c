/* Graph colouring: minimise the number of distinct colours.
   used[k] is forced true whenever some node takes colour k; the objective is the
   number of used colours, minimised by tightening. */
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
  int n = geti(inst, "n_nodes");
  cJSON *ej = cJSON_GetObjectItemCaseSensitive(inst, "edges");
  int m = cJSON_GetArraySize(ej);
  int *eu = malloc((m + 1) * sizeof *eu), *ev = malloc((m + 1) * sizeof *ev);
  for (int e = 0; e < m; e++) {
    cJSON *pair = cJSON_GetArrayItem(ej, e);
    eu[e] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(pair, 0));
    ev[e] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(pair, 1));
  }
  cJSON_Delete(inst);

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  /* c[i] is the colour of node i, in 0..n-1 (n colours always suffice) */
  term_t *c = malloc(n * sizeof *c);
  for (int i = 0; i < n; i++) {
    c[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_ok(ctx, yices_arith_geq_atom(c[i], yices_int32(0)));
    assert_ok(ctx, yices_arith_leq_atom(c[i], yices_int32(n - 1)));
  }

  /* adjacent nodes get different colours */
  for (int e = 0; e < m; e++)
    assert_ok(ctx, yices_arith_neq_atom(c[eu[e]], c[ev[e]]));

  /* used[k] is true whenever some node has colour k */
  term_t *used = malloc(n * sizeof *used);
  term_t *used01 = malloc(n * sizeof *used01);
  for (int k = 0; k < n; k++) {
    used[k] = chk(yices_new_uninterpreted_term(yices_bool_type()));
    for (int i = 0; i < n; i++)
      assert_ok(ctx, yices_implies(yices_arith_eq_atom(c[i], yices_int32(k)), used[k]));
    used01[k] = chk(yices_ite(used[k], yices_int32(1), yices_int32(0)));
  }
  term_t colours = chk(yices_sum(n, used01));

  int64_t best = n + 1;
  int *best_col = malloc(n * sizeof *best_col);
  int found = 0;
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    yices_get_int64_value(mdl, colours, &best);
    for (int i = 0; i < n; i++) {
      int64_t v = 0;
      yices_get_int64_value(mdl, c[i], &v);
      best_col[i] = (int)v;
    }
    yices_free_model(mdl);
    found = 1;
    assert_ok(ctx, yices_arith_lt_atom(colours, yices_int64(best)));
  }
  if (st != YICES_STATUS_UNSAT) {
    fprintf(stderr, "solver status %d\n", (int)st);
    return 1;
  }

  if (!found) {
    printf("{\"status\": \"unsatisfiable\"}\n");
  } else {
    printf("{\"colour\": [");
    for (int i = 0; i < n; i++) printf("%s%d", i ? ", " : "", best_col[i]);
    printf("]}\n");
  }

  yices_free_context(ctx);
  yices_exit();
  return 0;
}
