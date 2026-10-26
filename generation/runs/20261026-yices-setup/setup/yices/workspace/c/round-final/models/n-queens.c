/* N-queens: place n queens so that no two share a row, column or diagonal.
   One solution is printed as the 0-based column of the queen in each row. */
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
  int n = geti(inst, "n");
  cJSON_Delete(inst);

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  /* q[i] is the column of the queen in row i */
  term_t *q = malloc(n * sizeof *q);
  for (int i = 0; i < n; i++) {
    q[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_ok(ctx, yices_arith_geq_atom(q[i], yices_int32(0)));
    assert_ok(ctx, yices_arith_leq_atom(q[i], yices_int32(n - 1)));
  }

  /* no two queens share a column */
  assert_ok(ctx, yices_distinct(n, q));

  /* no two queens share a diagonal: the column difference is never the row difference */
  for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++) {
      int d = j - i;
      term_t diff = chk(yices_sub(q[i], q[j]));
      assert_ok(ctx, yices_arith_neq_atom(diff, yices_int32(d)));
      assert_ok(ctx, yices_arith_neq_atom(diff, yices_int32(-d)));
    }

  smt_status_t st = yices_check_context(ctx, NULL);
  if (st == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    printf("{\"queens\": [");
    for (int i = 0; i < n; i++) {
      int64_t v = 0;
      yices_get_int64_value(mdl, q[i], &v);
      printf("%s%lld", i ? ", " : "", (long long)v);
    }
    printf("]}\n");
    yices_free_model(mdl);
  } else if (st == YICES_STATUS_UNSAT) {
    printf("{\"status\": \"unsatisfiable\"}\n");
  } else {
    fprintf(stderr, "solver status %d\n", (int)st);
    return 1;
  }

  yices_free_context(ctx);
  yices_exit();
  return 0;
}
