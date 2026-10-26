/* Graph colouring: colour the nodes so that adjacent nodes differ, using as few
   colours as possible. Optimised by tightening the number of used colours.
   Usage: graph-colouring instance.json */
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
  int n = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "n_nodes"));
  cJSON *edges = cJSON_GetObjectItemCaseSensitive(root, "edges");
  int m = cJSON_GetArraySize(edges);

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t col[n];
  for (int i = 0; i < n; i++) {
    col[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    put(ctx, yices_arith_geq_atom(col[i], yices_int32(0)));
    put(ctx, yices_arith_leq_atom(col[i], yices_int32(n - 1)));
  }
  /* the endpoints of every edge get different colours */
  for (int e = 0; e < m; e++) {
    cJSON *ed = cJSON_GetArrayItem(edges, e);
    int u = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(ed, 0));
    int v = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(ed, 1));
    put(ctx, yices_arith_neq_atom(col[u], col[v]));
  }
  /* cost: number of colours k that some node uses */
  term_t used[n];
  for (int k = 0; k < n; k++) {
    term_t eqs[n];
    for (int i = 0; i < n; i++) eqs[i] = chk(yices_arith_eq_atom(col[i], yices_int32(k)));
    used[k] = chk(yices_ite(chk(yices_or(n, eqs)), yices_int32(1), yices_int32(0)));
  }
  term_t cost = chk(yices_sum(n, used));

  /* tighten until UNSAT: the last model is optimal */
  int64_t best = -1;
  int64_t bestcol[n];
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    yices_get_int64_value(mdl, cost, &best);
    for (int i = 0; i < n; i++) yices_get_int64_value(mdl, col[i], &bestcol[i]);
    yices_free_model(mdl);
    put(ctx, yices_arith_lt_atom(cost, chk(yices_int64(best))));
  }

  if (best >= 0) {
    printf("{\"colour\": [");
    for (int i = 0; i < n; i++) printf("%s%lld", i ? ", " : "", (long long)bestcol[i]);
    printf("]}\n");
  } else if (st == YICES_STATUS_UNSAT) {
    printf("{\"status\": \"unsatisfiable\"}\n");
  } else {
    fprintf(stderr, "solver status %d\n", (int)st);
    return 1;
  }

  yices_free_context(ctx);
  yices_exit();
  cJSON_Delete(root);
  return 0;
}
