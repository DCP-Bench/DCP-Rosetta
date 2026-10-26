/* Addition cryptarithm: assign distinct digits to letters so that the addends sum to the sum word.
   Each word is the weighted sum of its letters (10^position); leading letters of words longer
   than one letter are non-zero. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 2; }
  cJSON *inst = load(argv[1]);
  cJSON *aj = cJSON_GetObjectItemCaseSensitive(inst, "addends");
  int na = cJSON_GetArraySize(aj);
  const char **words = malloc((na + 1) * sizeof *words);
  int total_letters = 0;
  for (int i = 0; i < na; i++) {
    words[i] = cJSON_GetStringValue(cJSON_GetArrayItem(aj, i));
    total_letters += (int)strlen(words[i]);
  }
  words[na] = cJSON_GetStringValue(cJSON_GetObjectItemCaseSensitive(inst, "sum"));
  total_letters += (int)strlen(words[na]);

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  /* one digit variable per letter that appears, indexed by 'A'..'Z' */
  term_t lt[26];
  int present[26] = {0};
  for (int wi = 0; wi <= na; wi++)
    for (const char *p = words[wi]; *p; p++) {
      int idx = *p - 'A';
      if (!present[idx]) {
        present[idx] = 1;
        lt[idx] = chk(yices_new_uninterpreted_term(yices_int_type()));
        assert_ok(ctx, yices_arith_geq_atom(lt[idx], yices_int32(0)));
        assert_ok(ctx, yices_arith_leq_atom(lt[idx], yices_int32(9)));
      }
    }

  /* letters take distinct digits */
  term_t *letters = malloc(26 * sizeof *letters);
  int nl = 0;
  for (int idx = 0; idx < 26; idx++)
    if (present[idx]) letters[nl++] = lt[idx];
  if (nl > 1) assert_ok(ctx, yices_distinct(nl, letters));

  /* no word longer than one letter starts with 0 */
  for (int wi = 0; wi <= na; wi++) {
    size_t len = strlen(words[wi]);
    if (len > 1) assert_ok(ctx, yices_arith_neq_atom(lt[words[wi][0] - 'A'], yices_int32(0)));
  }

  /* sum of the addend values equals the sum value */
  term_t *lhs = malloc(total_letters * sizeof *lhs), *rhs = malloc(total_letters * sizeof *rhs);
  int nlhs = 0, nrhs = 0;
  for (int wi = 0; wi <= na; wi++) {
    size_t len = strlen(words[wi]);
    for (size_t p = 0; p < len; p++) {
      char ch = words[wi][len - 1 - p];
      int64_t coef = 1;
      for (size_t k = 0; k < p; k++) coef *= 10;
      term_t t = chk(yices_mul(yices_int64(coef), lt[ch - 'A']));
      if (wi < na) lhs[nlhs++] = t; else rhs[nrhs++] = t;
    }
  }
  assert_ok(ctx, yices_arith_eq_atom(chk(yices_sum(nlhs, lhs)), chk(yices_sum(nrhs, rhs))));

  smt_status_t st = yices_check_context(ctx, NULL);
  if (st == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    printf("{\"digits\": {");
    int first = 1;
    for (int idx = 0; idx < 26; idx++) {
      if (!present[idx]) continue;
      int64_t v = 0;
      yices_get_int64_value(mdl, lt[idx], &v);
      printf("%s\"%c\": %lld", first ? "" : ", ", 'A' + idx, (long long)v);
      first = 0;
    }
    printf("}}\n");
    yices_free_model(mdl);
  } else if (st == YICES_STATUS_UNSAT) {
    printf("{\"status\": \"unsatisfiable\"}\n");
  } else {
    fprintf(stderr, "solver status %d\n", (int)st);
    return 1;
  }

  cJSON_Delete(inst);
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
