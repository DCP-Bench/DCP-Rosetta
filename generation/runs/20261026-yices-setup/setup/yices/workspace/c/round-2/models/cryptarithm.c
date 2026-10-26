/* Addition cryptarithm: give each letter a distinct digit 0-9 so that the
   addends sum to the sum word; a word of more than one letter may not start
   with 0. Usage: cryptarithm instance.json */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

/* one digit variable per letter A-Z, created on first use */
static term_t var[26];
static int have[26];

/* the word read as a decimal number: sum of digit * 10^position */
static term_t word_value(const char *w) {
  int len = (int)strlen(w);
  term_t parts[len];
  int64_t p = 1;
  for (int k = len - 1; k >= 0; k--) {
    parts[k] = chk(yices_mul(chk(yices_int64(p)), var[w[k] - 'A']));
    p *= 10;
  }
  return chk(yices_sum(len, parts));
}

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 2; }
  cJSON *root = cJSON_Parse(slurp(argv[1]));
  if (!root) { fprintf(stderr, "bad JSON\n"); return 1; }
  cJSON *adds = cJSON_GetObjectItemCaseSensitive(root, "addends");
  int na = cJSON_GetArraySize(adds);
  const char *words[64];
  for (int i = 0; i < na; i++) words[i] = cJSON_GetStringValue(cJSON_GetArrayItem(adds, i));
  const char *sum = cJSON_GetStringValue(cJSON_GetObjectItemCaseSensitive(root, "sum"));

  yices_init();
  char order[26];
  int nl = 0;
  for (int i = 0; i <= na; i++) {
    const char *w = i < na ? words[i] : sum;
    for (const char *c = w; *c; c++) {
      int k = *c - 'A';
      if (!have[k]) {
        have[k] = 1;
        order[nl++] = *c;
        var[k] = chk(yices_new_uninterpreted_term(yices_int_type()));
      }
    }
  }

  context_t *ctx = yices_new_context(NULL);
  /* each letter is a digit */
  for (int i = 0; i < nl; i++) {
    term_t v = var[order[i] - 'A'];
    put(ctx, yices_arith_geq_atom(v, yices_int32(0)));
    put(ctx, yices_arith_leq_atom(v, yices_int32(9)));
  }
  /* different letters, different digits */
  if (nl >= 2) {
    term_t arr[26];
    for (int i = 0; i < nl; i++) arr[i] = var[order[i] - 'A'];
    put(ctx, chk(yices_distinct(nl, arr)));
  }
  /* no multi-letter word starts with 0 */
  for (int i = 0; i <= na; i++) {
    const char *w = i < na ? words[i] : sum;
    if (strlen(w) > 1) put(ctx, yices_arith_neq_atom(var[w[0] - 'A'], yices_int32(0)));
  }
  /* the addends add up to the sum */
  term_t lhs[64];
  for (int i = 0; i < na; i++) lhs[i] = word_value(words[i]);
  put(ctx, yices_arith_eq_atom(chk(yices_sum(na, lhs)), word_value(sum)));

  smt_status_t st = yices_check_context(ctx, NULL);
  if (st == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    printf("{\"digits\": {");
    for (int i = 0; i < nl; i++) {
      int64_t d = 0;
      yices_get_int64_value(mdl, var[order[i] - 'A'], &d);
      printf("%s\"%c\": %lld", i ? ", " : "", order[i], (long long)d);
    }
    printf("}}\n");
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
