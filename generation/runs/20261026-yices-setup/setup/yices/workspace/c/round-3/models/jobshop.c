/* Job-shop scheduling: minimise the makespan M. Each task starts at s[j][k];
   tasks of a job run in order; tasks on one machine never overlap. */
#include <stdio.h>
#include <stdlib.h>
#include <cjson/cJSON.h>
#include <yices.h>

#define MAXJ 32
#define MAXK 32

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

static int nj, jlen[MAXJ], mach[MAXJ][MAXK], dur[MAXJ][MAXK];
static term_t s[MAXJ][MAXK];
static int64_t sbest[MAXJ][MAXK];

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 1; }
  char *text = read_file(argv[1]);
  cJSON *root = cJSON_Parse(text);
  if (!root) { fprintf(stderr, "invalid JSON\n"); return 1; }
  cJSON *jobs = cJSON_GetObjectItemCaseSensitive(root, "jobs");
  nj = cJSON_GetArraySize(jobs);
  int64_t horizon = 0;
  for (int j = 0; j < nj; j++) {
    cJSON *job = cJSON_GetArrayItem(jobs, j);
    jlen[j] = cJSON_GetArraySize(job);
    for (int k = 0; k < jlen[j]; k++) {
      cJSON *task = cJSON_GetArrayItem(job, k);
      mach[j][k] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(task, 0));
      dur[j][k] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(task, 1));
      horizon += dur[j][k];
    }
  }

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  term_t M = chk(yices_new_uninterpreted_term(yices_int_type()));
  assert_(ctx, yices_arith_geq_atom(M, yices_int32(0)));

  for (int j = 0; j < nj; j++)
    for (int k = 0; k < jlen[j]; k++) {
      s[j][k] = chk(yices_new_uninterpreted_term(yices_int_type()));
      assert_(ctx, yices_arith_geq_atom(s[j][k], yices_int32(0)));
      assert_(ctx, yices_arith_leq_atom(s[j][k], yices_int32((int32_t)horizon)));
    }

  for (int j = 0; j < nj; j++)
    for (int k = 0; k < jlen[j]; k++) {
      /* A task ends no later than the makespan. */
      assert_(ctx, yices_arith_leq_atom(chk(yices_add(s[j][k], yices_int32(dur[j][k]))), M));
      /* Task k+1 of the same job starts after task k ends. */
      if (k + 1 < jlen[j])
        assert_(ctx, yices_arith_leq_atom(chk(yices_add(s[j][k], yices_int32(dur[j][k]))),
                                          s[j][k + 1]));
    }

  /* Tasks on the same machine do not overlap: one of them ends before the other starts. */
  for (int j1 = 0; j1 < nj; j1++)
    for (int k1 = 0; k1 < jlen[j1]; k1++)
      for (int j2 = j1; j2 < nj; j2++)
        for (int k2 = (j2 == j1 ? k1 + 1 : 0); k2 < jlen[j2]; k2++) {
          if (mach[j1][k1] != mach[j2][k2]) continue;
          term_t a_before_b = yices_arith_leq_atom(chk(yices_add(s[j1][k1], yices_int32(dur[j1][k1]))),
                                                   s[j2][k2]);
          term_t b_before_a = yices_arith_leq_atom(chk(yices_add(s[j2][k2], yices_int32(dur[j2][k2]))),
                                                   s[j1][k1]);
          assert_(ctx, yices_or2(a_before_b, b_before_a));
        }

  /* Minimise the makespan by tightening; keep the schedule of the last model. */
  int have = 0;
  int64_t best = 0;
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t mv;
    if (yices_get_int64_value(mdl, M, &mv) < 0) { yices_print_error(stderr); return 1; }
    for (int j = 0; j < nj; j++)
      for (int k = 0; k < jlen[j]; k++) {
        if (yices_get_int64_value(mdl, s[j][k], &sbest[j][k]) < 0) { yices_print_error(stderr); return 1; }
      }
    yices_free_model(mdl);
    best = mv;
    have = 1;
    assert_(ctx, yices_arith_lt_atom(M, yices_int32((int32_t)best)));
  }

  if (have) {
    printf("{\"start\": [");
    for (int j = 0; j < nj; j++) {
      printf("%s[", j ? ", " : "");
      for (int k = 0; k < jlen[j]; k++) printf("%s%lld", k ? ", " : "", (long long)sbest[j][k]);
      printf("]");
    }
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
