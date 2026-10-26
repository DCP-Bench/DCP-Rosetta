/* 0/1 knapsack: take items (x[i] in {0,1}) within capacity, maximising value. */
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
  cJSON *wj = cJSON_GetObjectItemCaseSensitive(root, "weights");
  cJSON *vj = cJSON_GetObjectItemCaseSensitive(root, "values");
  int n = cJSON_GetArraySize(wj);
  int cap = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "capacity"));

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  term_t x[64], wterms[64], vterms[64];
  for (int i = 0; i < n; i++) {
    int w = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(wj, i));
    int v = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(vj, i));
    x[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_(ctx, yices_arith_geq_atom(x[i], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(x[i], yices_int32(1)));
    wterms[i] = chk(yices_mul(yices_int32(w), x[i]));
    vterms[i] = chk(yices_mul(yices_int32(v), x[i]));
  }
  assert_(ctx, yices_arith_leq_atom(chk(yices_sum(n, wterms)), yices_int32(cap)));
  term_t obj = chk(yices_sum(n, vterms));

  /* Maximise by tightening; keep the selection of the last model. */
  int have = 0;
  int64_t best = 0;
  int take[64];
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t ov;
    if (yices_get_int64_value(mdl, obj, &ov) < 0) { yices_print_error(stderr); return 1; }
    for (int i = 0; i < n; i++) {
      int64_t t;
      if (yices_get_int64_value(mdl, x[i], &t) < 0) { yices_print_error(stderr); return 1; }
      take[i] = (int)t;
    }
    yices_free_model(mdl);
    best = ov;
    have = 1;
    assert_(ctx, yices_arith_gt_atom(obj, yices_int32((int32_t)best)));
  }

  if (have) {
    printf("{\"take\": [");
    for (int i = 0; i < n; i++) printf("%s%d", i ? ", " : "", take[i]);
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
