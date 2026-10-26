/* Graph colouring: colour the nodes so adjacent nodes differ, minimising the
   number of colours. u[j] = 1 when colour j is used; the objective is sum u[j]. */
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

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 1; }
  char *text = read_file(argv[1]);
  cJSON *root = cJSON_Parse(text);
  if (!root) { fprintf(stderr, "invalid JSON\n"); return 1; }
  int n = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "n_nodes"));
  cJSON *edges = cJSON_GetObjectItemCaseSensitive(root, "edges");
  int ne = cJSON_GetArraySize(edges);

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  term_t c[64], u[64];
  for (int i = 0; i < n; i++) {
    c[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_(ctx, yices_arith_geq_atom(c[i], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(c[i], yices_int32(n - 1)));
  }
  for (int j = 0; j < n; j++) {
    u[j] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_(ctx, yices_arith_geq_atom(u[j], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(u[j], yices_int32(1)));
  }

  /* Adjacent nodes get different colours. */
  for (int e = 0; e < ne; e++) {
    cJSON *pair = cJSON_GetArrayItem(edges, e);
    int a = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(pair, 0));
    int b = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(pair, 1));
    assert_(ctx, yices_arith_neq_atom(c[a], c[b]));
  }

  /* Colour j used by node i forces u[j] = 1. */
  for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
      assert_(ctx, yices_implies(yices_arith_eq_atom(c[i], yices_int32(j)),
                                 yices_arith_eq_atom(u[j], yices_int32(1))));

  term_t obj = chk(yices_sum(n, u));

  /* Minimise by tightening; keep the colouring of the last (best) model. */
  int64_t best = 0;
  int have = 0;
  int bestcol[64];
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t ov;
    if (yices_get_int64_value(mdl, obj, &ov) < 0) { yices_print_error(stderr); return 1; }
    for (int i = 0; i < n; i++) {
      int64_t v;
      if (yices_get_int64_value(mdl, c[i], &v) < 0) { yices_print_error(stderr); return 1; }
      bestcol[i] = (int)v;
    }
    yices_free_model(mdl);
    best = ov;
    have = 1;
    assert_(ctx, yices_arith_lt_atom(obj, yices_int32((int32_t)best)));
  }

  if (have) {
    printf("{\"colour\": [");
    for (int i = 0; i < n; i++) printf("%s%d", i ? ", " : "", bestcol[i]);
    printf("]}\n");
  } else {
    printf("{\"status\": \"unsatisfiable\"}\n");
  }

  yices_free_context(ctx);
  cJSON_Delete(root);
  free(text);
  yices_exit();
  return 0;
}
