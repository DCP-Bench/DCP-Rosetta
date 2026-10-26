/* All n-queens solutions: same model as n-queens, then enumerate every
 * placement by asserting a no-good over the queen columns after each model
 * until the context becomes UNSAT. Prints one {"queens": [...]} per line. */
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
  int n = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(inst, "n"));

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t *q = malloc(sizeof(term_t) * (size_t)n);
  for (int i = 0; i < n; i++) {
    q[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_f(ctx, yices_arith_geq_atom(q[i], yices_int32(0)));
    assert_f(ctx, yices_arith_leq_atom(q[i], yices_int32(n - 1)));
  }
  assert_f(ctx, yices_distinct((uint32_t)n, q));
  for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++) {
      int d = j - i;
      term_t diff = chk(yices_sub(q[i], q[j]));
      assert_f(ctx, yices_arith_neq_atom(diff, yices_int32(d)));
      assert_f(ctx, yices_arith_neq_atom(diff, yices_int32(-d)));
    }

  term_t *differs = malloc(sizeof(term_t) * (size_t)n);
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    printf("{\"queens\": [");
    for (int i = 0; i < n; i++) {
      int64_t v = get_int(mdl, q[i]);
      printf("%s%lld", i ? ", " : "", (long long)v);
      differs[i] = chk(yices_arith_neq_atom(q[i], yices_int64(v)));
    }
    printf("]}\n");
    yices_free_model(mdl);
    assert_f(ctx, yices_or((uint32_t)n, differs));
  }
  if (st != YICES_STATUS_UNSAT) {
    fprintf(stderr, "unexpected status %d\n", (int)st);
    return 1;
  }
  yices_free_context(ctx);
  cJSON_Delete(inst);
  yices_exit();
  return 0;
}
