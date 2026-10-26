/* Job-shop scheduling: minimise the makespan.
 * s[j][k] = start of task k of job j (integer, 0..H with H the sum of all
 * durations). Tasks of one job follow each other; tasks on the same machine
 * do not overlap (pairwise disjunction). mk >= end of every job's last task.
 * The makespan is minimised by tightening mk until UNSAT.
 * Prints one optimal {"start": [[...], ...]} on stdout. */
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
  cJSON *jobs = cJSON_GetObjectItemCaseSensitive(inst, "jobs");
  int nj = cJSON_GetArraySize(jobs);
  int *nt = malloc(sizeof(int) * (size_t)nj);
  int **mach = malloc(sizeof(int *) * (size_t)nj);
  int **dur = malloc(sizeof(int *) * (size_t)nj);
  int64_t horizon = 0;
  for (int j = 0; j < nj; j++) {
    cJSON *job = cJSON_GetArrayItem(jobs, j);
    nt[j] = cJSON_GetArraySize(job);
    mach[j] = malloc(sizeof(int) * (size_t)nt[j]);
    dur[j] = malloc(sizeof(int) * (size_t)nt[j]);
    for (int k = 0; k < nt[j]; k++) {
      cJSON *task = cJSON_GetArrayItem(job, k);
      mach[j][k] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(task, 0));
      dur[j][k] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(task, 1));
      horizon += dur[j][k];
    }
  }

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t mk = chk(yices_new_uninterpreted_term(yices_int_type()));
  assert_f(ctx, yices_arith_geq_atom(mk, yices_int32(0)));
  assert_f(ctx, yices_arith_leq_atom(mk, yices_int64(horizon)));

  term_t **s = malloc(sizeof(term_t *) * (size_t)nj);
  for (int j = 0; j < nj; j++) {
    s[j] = malloc(sizeof(term_t) * (size_t)nt[j]);
    for (int k = 0; k < nt[j]; k++) {
      s[j][k] = chk(yices_new_uninterpreted_term(yices_int_type()));
      assert_f(ctx, yices_arith_geq_atom(s[j][k], yices_int32(0)));
      assert_f(ctx, yices_arith_leq_atom(s[j][k], yices_int64(horizon)));
    }
    /* job order: task k+1 starts after task k ends */
    for (int k = 0; k + 1 < nt[j]; k++)
      assert_f(ctx, yices_arith_geq_atom(yices_sub(s[j][k + 1], s[j][k]), yices_int32(dur[j][k])));
    /* makespan is at least the end of each job */
    int last = nt[j] - 1;
    assert_f(ctx, yices_arith_geq_atom(mk, yices_add(s[j][last], yices_int32(dur[j][last]))));
  }

  /* tasks on one machine do not overlap */
  for (int j1 = 0; j1 < nj; j1++)
    for (int k1 = 0; k1 < nt[j1]; k1++)
      for (int j2 = j1; j2 < nj; j2++)
        for (int k2 = 0; k2 < nt[j2]; k2++) {
          if (j2 == j1 && k2 <= k1) continue;
          if (mach[j1][k1] != mach[j2][k2]) continue;
          term_t a_before_b = chk(yices_arith_leq_atom(
              yices_add(s[j1][k1], yices_int32(dur[j1][k1])), s[j2][k2]));
          term_t b_before_a = chk(yices_arith_leq_atom(
              yices_add(s[j2][k2], yices_int32(dur[j2][k2])), s[j1][k1]));
          assert_f(ctx, yices_or2(a_before_b, b_before_a));
        }

  int64_t **best = malloc(sizeof(int64_t *) * (size_t)nj);
  for (int j = 0; j < nj; j++) best[j] = malloc(sizeof(int64_t) * (size_t)nt[j]);
  int found = 0;
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t span = get_int(mdl, mk);
    for (int j = 0; j < nj; j++)
      for (int k = 0; k < nt[j]; k++) best[j][k] = get_int(mdl, s[j][k]);
    yices_free_model(mdl);
    found = 1;
    assert_f(ctx, yices_arith_lt_atom(mk, yices_int64(span)));
  }
  if (st != YICES_STATUS_UNSAT || !found) {
    fprintf(stderr, "no optimal schedule found (status %d)\n", (int)st);
    return 1;
  }
  printf("{\"start\": [");
  for (int j = 0; j < nj; j++) {
    printf("%s[", j ? ", " : "");
    for (int k = 0; k < nt[j]; k++) printf("%s%lld", k ? ", " : "", (long long)best[j][k]);
    printf("]");
  }
  printf("]}\n");
  yices_free_context(ctx);
  cJSON_Delete(inst);
  yices_exit();
  return 0;
}
