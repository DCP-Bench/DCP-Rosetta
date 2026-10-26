/* Job-shop scheduling: minimise the makespan.
   Start times are integers in 0..horizon; each job's tasks follow their order; tasks on the same
   machine do not overlap. The makespan is tightened: each SAT model asserts every job ends
   before the makespan found. */
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

int main(int argc, char **argv) {
  if (argc < 2) { fprintf(stderr, "usage: %s instance.json\n", argv[0]); return 2; }
  cJSON *inst = load(argv[1]);
  cJSON *jobs = cJSON_GetObjectItemCaseSensitive(inst, "jobs");
  int nj = cJSON_GetArraySize(jobs);
  int *nt = malloc(nj * sizeof *nt);
  int **mach = malloc(nj * sizeof *mach), **dur = malloc(nj * sizeof *dur);
  int horizon = 0, ntasks = 0;
  for (int j = 0; j < nj; j++) {
    cJSON *job = cJSON_GetArrayItem(jobs, j);
    nt[j] = cJSON_GetArraySize(job);
    mach[j] = malloc(nt[j] * sizeof **mach);
    dur[j] = malloc(nt[j] * sizeof **dur);
    for (int k = 0; k < nt[j]; k++) {
      cJSON *pair = cJSON_GetArrayItem(job, k);
      mach[j][k] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(pair, 0));
      dur[j][k] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(pair, 1));
      horizon += dur[j][k];
      ntasks++;
    }
  }
  cJSON_Delete(inst);

  yices_init();
  context_t *ctx = yices_new_context(NULL);

  /* s[j][k] is the start of task k of job j */
  term_t **s = malloc(nj * sizeof *s);
  for (int j = 0; j < nj; j++) {
    s[j] = malloc(nt[j] * sizeof **s);
    for (int k = 0; k < nt[j]; k++) {
      s[j][k] = chk(yices_new_uninterpreted_term(yices_int_type()));
      assert_ok(ctx, yices_arith_geq_atom(s[j][k], yices_int32(0)));
      assert_ok(ctx, yices_arith_leq_atom(s[j][k], yices_int32(horizon)));
    }
  }

  /* job order: each task starts after the previous one of its job ends */
  for (int j = 0; j < nj; j++)
    for (int k = 0; k + 1 < nt[j]; k++)
      assert_ok(ctx, yices_arith_geq_atom(
          chk(yices_sub(s[j][k + 1], s[j][k])), yices_int32(dur[j][k])));

  /* machines: two tasks on one machine do not overlap */
  term_t *ts = malloc(ntasks * sizeof *ts);
  term_t *te = malloc(ntasks * sizeof *te);
  int *tj = malloc(ntasks * sizeof *tj), *tk = malloc(ntasks * sizeof *tk);
  int T = 0;
  for (int j = 0; j < nj; j++)
    for (int k = 0; k < nt[j]; k++) {
      tj[T] = j; tk[T] = k; ts[T] = s[j][k];
      te[T] = chk(yices_add(s[j][k], yices_int32(dur[j][k])));
      T++;
    }
  for (int a = 0; a < T; a++)
    for (int b = a + 1; b < T; b++) {
      if (mach[tj[a]][tk[a]] != mach[tj[b]][tk[b]]) continue;
      term_t a_first = yices_arith_leq_atom(te[a], ts[b]);
      term_t b_first = yices_arith_leq_atom(te[b], ts[a]);
      assert_ok(ctx, yices_or2(a_first, b_first));
    }

  /* the makespan is the latest end over all jobs */
  term_t *last_end = malloc(nj * sizeof *last_end);
  for (int j = 0; j < nj; j++)
    last_end[j] = chk(yices_add(s[j][nt[j] - 1], yices_int32(dur[j][nt[j] - 1])));

  /* best schedule so far: start[j][k] */
  int **best = malloc(nj * sizeof *best);
  for (int j = 0; j < nj; j++) best[j] = malloc(nt[j] * sizeof **best);
  int found = 0;
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    int64_t makespan = 0;
    for (int j = 0; j < nj; j++) {
      int64_t e = 0;
      yices_get_int64_value(mdl, last_end[j], &e);
      if (e > makespan) makespan = e;
      for (int k = 0; k < nt[j]; k++) {
        int64_t v = 0;
        yices_get_int64_value(mdl, s[j][k], &v);
        best[j][k] = (int)v;
      }
    }
    yices_free_model(mdl);
    found = 1;
    for (int j = 0; j < nj; j++)
      assert_ok(ctx, yices_arith_leq_atom(last_end[j], yices_int64(makespan - 1)));
  }
  if (st != YICES_STATUS_UNSAT) {
    fprintf(stderr, "solver status %d\n", (int)st);
    return 1;
  }

  if (!found) {
    printf("{\"status\": \"unsatisfiable\"}\n");
  } else {
    printf("{\"start\": [");
    for (int j = 0; j < nj; j++) {
      printf("%s[", j ? ", " : "");
      for (int k = 0; k < nt[j]; k++) printf("%s%d", k ? ", " : "", best[j][k]);
      printf("]");
    }
    printf("]}\n");
  }

  yices_free_context(ctx);
  yices_exit();
  return 0;
}
