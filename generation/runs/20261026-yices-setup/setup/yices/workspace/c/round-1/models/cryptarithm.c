/* Addition cryptarithm: assign a digit 0-9 to each letter so that the sum of
 * the addends, read as decimal numbers, equals the sum word. Distinct letters
 * get distinct digits; a word longer than one letter has a nonzero first letter.
 * Prints one solution as {"digits": {...}} or {"status": "unsatisfiable"}. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

/* one digit variable per letter */
static term_t digit[256];
static int letter_index[256];
static char letters[256];
static int n_letters = 0;

/* value of a word: sum of digit * 10^position */
static term_t word_value(const char *w) {
  size_t len = strlen(w);
  term_t *parts = malloc(sizeof(term_t) * len);
  int64_t place = 1;
  for (size_t j = 0; j < len; j++) {
    unsigned char c = (unsigned char)w[len - 1 - j];
    parts[j] = chk(yices_mul(yices_int64(place), digit[c]));
    place *= 10;
  }
  return chk(yices_sum((uint32_t)len, parts));
}

int main(int argc, char **argv) {
  if (argc != 2) { fprintf(stderr, "usage: %s INSTANCE.json\n", argv[0]); return 2; }
  cJSON *inst = cJSON_Parse(read_file(argv[1]));
  if (!inst) { fprintf(stderr, "invalid JSON\n"); return 2; }
  cJSON *addends = cJSON_GetObjectItemCaseSensitive(inst, "addends");
  const char *sum_word = cJSON_GetStringValue(cJSON_GetObjectItemCaseSensitive(inst, "sum"));
  int n_add = cJSON_GetArraySize(addends);
  const char **words = malloc(sizeof(char *) * (size_t)(n_add + 1));
  for (int i = 0; i < n_add; i++) words[i] = cJSON_GetStringValue(cJSON_GetArrayItem(addends, i));
  words[n_add] = sum_word;
  int n_words = n_add + 1;

  /* collect the distinct letters of all words */
  for (int c = 0; c < 256; c++) letter_index[c] = -1;
  for (int w = 0; w < n_words; w++)
    for (const char *p = words[w]; *p; p++) {
      unsigned char c = (unsigned char)*p;
      if (letter_index[c] < 0) { letter_index[c] = n_letters; letters[n_letters++] = (char)c; }
    }

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t *dv = malloc(sizeof(term_t) * (size_t)n_letters);
  for (int k = 0; k < n_letters; k++) {
    dv[k] = chk(yices_new_uninterpreted_term(yices_int_type()));
    assert_f(ctx, yices_arith_geq_atom(dv[k], yices_int32(0)));
    assert_f(ctx, yices_arith_leq_atom(dv[k], yices_int32(9)));
    digit[(unsigned char)letters[k]] = dv[k];
  }
  assert_f(ctx, yices_distinct((uint32_t)n_letters, dv));
  /* no word of more than one letter starts with 0 */
  for (int w = 0; w < n_words; w++)
    if (strlen(words[w]) > 1)
      assert_f(ctx, yices_arith_neq_atom(digit[(unsigned char)words[w][0]], yices_int32(0)));

  /* sum of addends equals the sum word */
  term_t *addvals = malloc(sizeof(term_t) * (size_t)n_add);
  for (int i = 0; i < n_add; i++) addvals[i] = word_value(words[i]);
  term_t total = chk(yices_sum((uint32_t)n_add, addvals));
  assert_f(ctx, yices_arith_eq_atom(total, word_value(sum_word)));

  smt_status_t st = yices_check_context(ctx, NULL);
  if (st == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    printf("{\"digits\": {");
    for (int k = 0; k < n_letters; k++)
      printf("%s\"%c\": %lld", k ? ", " : "", letters[k], (long long)get_int(mdl, dv[k]));
    printf("}}\n");
    yices_free_model(mdl);
  } else if (st == YICES_STATUS_UNSAT) {
    printf("{\"status\": \"unsatisfiable\"}\n");
  } else {
    fprintf(stderr, "unexpected status %d\n", (int)st);
    return 1;
  }
  yices_free_context(ctx);
  cJSON_Delete(inst);
  yices_exit();
  return 0;
}
