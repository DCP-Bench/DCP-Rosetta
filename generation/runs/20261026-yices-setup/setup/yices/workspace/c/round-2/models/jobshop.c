/* Job-shop scheduling: each job's tasks run in order, each task holds its machine
   for its duration, a machine runs one task at a time; minimise the makespan.
   Optimised by tightening the makespan bound. Usage: jobshop instance.json */
#include <stdio.h>
#include <stdlib.h>
#include <cjson/cJSON.h>
#include <yices.h>

#define MAXT 1024   /* total number of tasks the model accepts */

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
  cJSON *jobs = cJSON_GetObjectItemCaseSensitive(root, "jobs");
  int nj = cJSON_GetArraySize(jobs);

  /* flatten the tasks: task t = job j, step k, with offset[j] + k */
  int njk[nj], offset[nj];
  int mach[MAXT], dur[MAXT];
  int total = 0, horizon = 0;
  for (int j = 0; j < nj; j++) {
    cJSON *job = cJSON_GetArrayItem(jobs, j);
    njk[j] = cJSON_GetArraySize(job);
    offset[j] = total;
    for (int k = 0; k < njk[j]; k++) {
      cJSON *task = cJSON_GetArrayItem(job, k);
      mach[total] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(task, 0));
      dur[total] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(task, 1));
      horizon += dur[total];
      total++;
    }
  }
  if (total > MAXT) { fprintf(stderr, "too many tasks\n"); return 1; }

  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t s[MAXT];
  for (int t = 0; t < total; t++) {
    s[t] = chk(yices_new_uninterpreted_term(yices_int_type()));
    put(ctx, yices_arith_geq_atom(s[t], yices_int32(0)));
    put(ctx, yices_arith_leq_atom(s[t], yices_int32(horizon)));
  }
  term_t makespan = chk(yices_new_uninterpreted_term(yices_int_type()));
  put(ctx, yices_arith_leq_atom(makespan, yices_int32(horizon)));

  /* precedence inside each job; the last task ends by the makespan */
  for (int j = 0; j < nj; j++)
    for (int k = 0; k < njk[j]; k++) {
      int t = offset[j] + k;
      term_t end = chk(yices_add(s[t], chk(yices_int64(dur[t]))));
      if (k + 1 < njk[j]) put(ctx, yices_arith_leq_atom(end, s[t + 1]));
      else put(ctx, yices_arith_leq_atom(end, makespan));
    }

  /* a machine runs one task at a time: for every pair on the same machine,
     one ends before the other starts */
  for (int a = 0; a < total; a++)
    for (int b = a + 1; b < total; b++)
      if (mach[a] == mach[b]) {
        term_t a_first = chk(yices_arith_leq_atom(chk(yices_add(s[a], chk(yices_int64(dur[a])))), s[b]));
        term_t b_first = chk(yices_arith_leq_atom(chk(yices_add(s[b], chk(yices_int64(dur[b])))), s[a]));
        put(ctx, chk(yices_or2(a_first, b_first)));
      }

  /* tighten the makespan until UNSAT: the last schedule is optimal */
  int64_t best = -1;
  int64_t start[MAXT];
  smt_status_t st;
  while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    yices_get_int64_value(mdl, makespan, &best);
    for (int t = 0; t < total; t++) yices_get_int64_value(mdl, s[t], &start[t]);
    yices_free_model(mdl);
    put(ctx, yices_arith_lt_atom(makespan, chk(yices_int64(best))));
  }
  if (best < 0) { fprintf(stderr, "solver status %d\n", (int)st); return 1; }

  printf("{\"start\": [");
  for (int j = 0; j < nj; j++) {
    printf("%s[", j ? ", " : "");
    for (int k = 0; k < njk[j]; k++)
      printf("%s%lld", k ? ", " : "", (long long)start[offset[j] + k]);
    printf("]");
  }
  printf("]}\n");

  yices_free_context(ctx);
  yices_exit();
  cJSON_Delete(root);
  return 0;
}
