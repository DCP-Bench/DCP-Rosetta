/* All n-queens placements: same model as n-queens, enumerated with no-goods
   over the column terms until UNSAT. */
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
  int n = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "n"));

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  term_t c[64];
  for (int i = 0; i < n; i++) {
    c[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_(ctx, yices_arith_geq_atom(c[i], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(c[i], yices_int32(n - 1)));
  }
  if (n >= 2) assert_(ctx, yices_distinct(n, c));
  for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++) {
      term_t d = chk(yices_sub(c[i], c[j]));
      assert_(ctx, yices_arith_neq_atom(d, yices_int32(i - j)));
      assert_(ctx, yices_arith_neq_atom(d, yices_int32(j - i)));
    }

  /* Enumerate: after each model, forbid exactly that placement. */
  term_t differs[64];
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t v[64];
    for (int i = 0; i < n; i++)
      if (yices_get_int64_value(mdl, c[i], &v[i]) < 0) { yices_print_error(stderr); return 1; }
    yices_free_model(mdl);

    printf("{\"queens\": [");
    for (int i = 0; i < n; i++) {
      printf("%s%lld", i ? ", " : "", (long long)v[i]);
      differs[i] = yices_arith_neq_atom(c[i], yices_int64(v[i]));
    }
    printf("]}\n");

    assert_(ctx, yices_or(n, differs));
  }

  yices_free_context(ctx);
  cJSON_Delete(root);
  free(text);
  yices_exit();
  return 0;
}
