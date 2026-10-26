/* Addition cryptarithm: a digit 0-9 for each letter, all letters distinct,
   no multi-letter word starts with 0, and the addends sum to the sum word. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

static char letters[64];
static term_t var[64];
static int nletters = 0;

static int letter_slot(char c) {
  for (int i = 0; i < nletters; i++)
    if (letters[i] == c) return i;
  letters[nletters] = c;
  return nletters++;
}

/* The value of a word: sum of digit * 10^position, as a linear term. */
static term_t word_value(const char *w) {
  int len = (int)strlen(w);
  term_t parts[16];
  int64_t place = 1;
  for (int p = len - 1; p >= 0; p--) {
    parts[p] = chk(yices_mul(yices_int64(place), var[letter_slot(w[p])]));
    place *= 10;
  }
  return chk(yices_sum(len, parts));
}

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 1; }
  char *text = read_file(argv[1]);
  cJSON *root = cJSON_Parse(text);
  if (!root) { fprintf(stderr, "invalid JSON\n"); return 1; }
  cJSON *adds = cJSON_GetObjectItemCaseSensitive(root, "addends");
  const char *sumw = cJSON_GetStringValue(cJSON_GetObjectItemCaseSensitive(root, "sum"));
  int nadd = cJSON_GetArraySize(adds);

  /* Collect the letters of every word, in order of first appearance. */
  const char *words[64];
  int nw = 0;
  for (int i = 0; i < nadd; i++) words[nw++] = cJSON_GetStringValue(cJSON_GetArrayItem(adds, i));
  words[nw++] = sumw;
  for (int w = 0; w < nw; w++)
    for (const char *p = words[w]; *p; p++) letter_slot(*p);

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  /* One digit per letter. */
  for (int k = 0; k < nletters; k++) {
    var[k] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_(ctx, yices_arith_geq_atom(var[k], yices_int32(0)));
    assert_(ctx, yices_arith_leq_atom(var[k], yices_int32(9)));
  }
  if (nletters >= 2) assert_(ctx, yices_distinct(nletters, var));

  /* A leading digit of a multi-letter word is not 0. */
  for (int w = 0; w < nw; w++) {
    int len = (int)strlen(words[w]);
    if (len > 1)
      assert_(ctx, yices_arith_geq_atom(var[letter_slot(words[w][0])], yices_int32(1)));
  }

  /* Sum of the addends equals the sum word. */
  term_t addend_values[64];
  for (int i = 0; i < nadd; i++) addend_values[i] = word_value(words[i]);
  term_t lhs = chk(yices_sum(nadd, addend_values));
  assert_(ctx, yices_arith_eq_atom(lhs, word_value(sumw)));

  smt_status_t st = yices_check_context(ctx, NULL);
  if (st == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    printf("{\"digits\": {");
    for (int k = 0; k < nletters; k++) {
      int64_t v;
      if (yices_get_int64_value(mdl, var[k], &v) < 0) { yices_print_error(stderr); return 1; }
      printf("%s\"%c\": %lld", k ? ", " : "", letters[k], (long long)v);
    }
    printf("}}\n");
    yices_free_model(mdl);
  } else {
    printf("{\"status\": \"unsatisfiable\"}\n");
  }

  yices_free_context(ctx);
  cJSON_Delete(root);
  free(text);
  yices_exit();
  return 0;
}
