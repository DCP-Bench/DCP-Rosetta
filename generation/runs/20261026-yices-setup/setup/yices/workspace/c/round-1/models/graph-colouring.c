/* Graph colouring: minimise the number of distinct colours.
 * Colour c[i] in 0..n-1; used[k] is forced true when some node has colour k;
 * the cost is the number of true used[k]. Optimise by tightening the bound
 * until UNSAT. Prints one optimal {"colour": [...]} on stdout. */
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
  int n = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(inst, "n_nodes"));
  cJSON *edges = cJSON_GetObjectItemCaseSensitive(inst, "edges");

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t *c = malloc(sizeof(term_t) * (size_t)n);
  term_t *used = malloc(sizeof(term_t) * (size_t)n);
  for (int i = 0; i < n; i++) {
    c[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_f(ctx, yices_arith_geq_atom(c[i], yices_int32(0)));
    assert_f(ctx, yices_arith_leq_atom(c[i], yices_int32(n - 1)));
  }
  for (int k = 0; k < n; k++) used[k] = chk(yices_new_uninterpreted_term(yices_bool_type()));

  /* adjacent nodes get different colours */
  for (int e = 0; e < cJSON_GetArraySize(edges); e++) {
    cJSON *edge = cJSON_GetArrayItem(edges, e);
    int a = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(edge, 0));
    int b = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(edge, 1));
    assert_f(ctx, yices_arith_neq_atom(c[a], c[b]));
  }
  /* a colour in use marks its usage flag */
  for (int i = 0; i < n; i++)
    for (int k = 0; k < n; k++)
      assert_f(ctx, yices_implies(yices_arith_eq_atom(c[i], yices_int32(k)), used[k]));
  /* symmetry: colours used form a prefix 0..m-1 */
  for (int k = 1; k < n; k++) assert_f(ctx, yices_implies(used[k], used[k - 1]));

  term_t *ones = malloc(sizeof(term_t) * (size_t)n);
  for (int k = 0; k < n; k++)
    ones[k] = chk(yices_ite(used[k], yices_int32(1), yices_int32(0)));
  term_t cost = chk(yices_sum((uint32_t)n, ones));

  int64_t *best_col = malloc(sizeof(int64_t) * (size_t)n);
  int found = 0;
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t cv = get_int(mdl, cost);
    for (int i = 0; i < n; i++) best_col[i] = get_int(mdl, c[i]);
    yices_free_model(mdl);
    found = 1;
    assert_f(ctx, yices_arith_lt_atom(cost, yices_int64(cv)));
  }
  if (st != YICES_STATUS_UNSAT || !found) {
    fprintf(stderr, "no optimal colouring found (status %d)\n", (int)st);
    return 1;
  }
  printf("{\"colour\": [");
  for (int i = 0; i < n; i++) printf("%s%lld", i ? ", " : "", (long long)best_col[i]);
  printf("]}\n");
  yices_free_context(ctx);
  cJSON_Delete(inst);
  yices_exit();
  return 0;
}
