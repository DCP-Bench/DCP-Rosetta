/* N-queens: place n queens, one per row, on an n x n board so that no two
   share a column or a diagonal. Usage: n-queens instance.json */
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
  int n = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "n"));

  yices_init();
  term_t q[n];
  context_t *ctx = yices_new_context(NULL);

  /* the queen in row i stands in column q[i], between 0 and n-1 */
  for (int i = 0; i < n; i++) {
    q[i] = chk(yices_new_uninterpreted_term(yices_int_type()));
    put(ctx, yices_arith_geq_atom(q[i], yices_int32(0)));
    put(ctx, yices_arith_leq_atom(q[i], yices_int32(n - 1)));
  }
  /* no two queens share a column */
  if (n >= 2) put(ctx, chk(yices_distinct(n, q)));
  /* no two queens share a diagonal: |q_i - q_j| differs from |i - j| */
  for (int i = 0; i < n; i++)
    for (int j = i + 1; j < n; j++) {
      term_t d = chk(yices_sub(q[i], q[j]));
      put(ctx, yices_arith_neq_atom(d, yices_int32(i - j)));
      put(ctx, yices_arith_neq_atom(d, yices_int32(j - i)));
    }

  smt_status_t st = yices_check_context(ctx, NULL);
  if (st == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    printf("{\"queens\": [");
    for (int i = 0; i < n; i++) {
      int64_t c = 0;
      yices_get_int64_value(mdl, q[i], &c);
      printf("%s%lld", i ? ", " : "", (long long)c);
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
  cJSON_Delete(root);
  return 0;
}
