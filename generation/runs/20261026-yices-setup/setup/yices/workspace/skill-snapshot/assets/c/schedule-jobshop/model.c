/* Job shop: 3 jobs, 3 machines. Each job runs its operations in order; a machine runs one
   operation at a time. Minimise the makespan with a time limit. */
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <yices.h>

#define J 3
#define K 3
static const int MACHINE[J][K] = {{1, 0, 2}, {0, 2, 1}, {2, 1, 0}};
static const int DUR[J][K]     = {{2, 3, 1}, {3, 2, 2}, {1, 4, 0}};  /* job 3 has 2 operations: duration 0 means absent */
#define TIME_LIMIT_SECONDS 10

static term_t chk(term_t t) {
  if (t < 0) { yices_print_error(stderr); exit(1); }
  return t;
}
static void assert_(context_t *ctx, term_t f) {
  if (yices_assert_formula(ctx, chk(f)) < 0) { yices_print_error(stderr); exit(1); }
}

/* Time limit: Yices has no time parameter. A timer signal calls yices_stop_search, which is
   documented as safe inside a signal handler. The check then returns INTERRUPTED. */
static context_t *running;
static void on_alarm(int sig) { (void)sig; yices_stop_search(running); }

static smt_status_t check_within(context_t *ctx, double seconds) {
  struct itimerval t = {{0, 0}, {(time_t)seconds, (suseconds_t)((seconds - (time_t)seconds) * 1e6)}};
  running = ctx;
  signal(SIGALRM, on_alarm);
  setitimer(ITIMER_REAL, &t, NULL);
  smt_status_t st = yices_check_context(ctx, NULL);
  struct itimerval off = {{0, 0}, {0, 0}};
  setitimer(ITIMER_REAL, &off, NULL);
  return st;
}

int main(void) {
  yices_init();
  context_t *ctx = yices_new_context(NULL);
  term_t start[J][K], makespan = yices_new_uninterpreted_term(yices_int_type());
  const int horizon = 40;
  assert_(ctx, yices_arith_geq_atom(makespan, yices_int32(0)));
  assert_(ctx, yices_arith_leq_atom(makespan, yices_int32(horizon)));
  for (int j = 0; j < J; j++)
    for (int k = 0; k < K; k++) {
      if (DUR[j][k] == 0) continue;
      start[j][k] = yices_new_uninterpreted_term(yices_int_type());
      assert_(ctx, yices_arith_geq_atom(start[j][k], yices_int32(0)));
      /* the operation ends before the makespan */
      assert_(ctx, yices_arith_leq_atom(yices_add(start[j][k], yices_int32(DUR[j][k])), makespan));
      /* precedence inside the job */
      if (k > 0 && DUR[j][k - 1] > 0)
        assert_(ctx, yices_arith_leq_atom(yices_add(start[j][k - 1], yices_int32(DUR[j][k - 1])), start[j][k]));
    }
  /* a machine runs one operation at a time: one ends before the other starts */
  for (int a = 0; a < J * K; a++)
    for (int b = a + 1; b < J * K; b++) {
      int ja = a / K, ka = a % K, jb = b / K, kb = b % K;
      if (DUR[ja][ka] == 0 || DUR[jb][kb] == 0 || MACHINE[ja][ka] != MACHINE[jb][kb]) continue;
      term_t either[2] = {
        yices_arith_leq_atom(yices_add(start[ja][ka], yices_int32(DUR[ja][ka])), start[jb][kb]),
        yices_arith_leq_atom(yices_add(start[jb][kb], yices_int32(DUR[jb][kb])), start[ja][ka])};
      assert_(ctx, yices_or(2, either));
    }

  int64_t best = -1;
  smt_status_t status;
  while ((status = check_within(ctx, TIME_LIMIT_SECONDS)) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);
    yices_get_int64_value(mdl, makespan, &best);
    yices_free_model(mdl);
    assert_(ctx, yices_arith_lt_atom(makespan, yices_int64(best)));
  }
  if (status == YICES_STATUS_UNSAT && best >= 0) {
    printf("Makespan: %lld (optimal)\n", (long long)best);
  } else if (status == YICES_STATUS_INTERRUPTED) {
    /* Time limit hit: the context needs a reset before reuse; best (if any) is not proven. */
    yices_reset_context(ctx);
    if (best >= 0) printf("Makespan: %lld (best found, not proven)\n", (long long)best);
    else printf("No solution within the time limit\n");
  } else {
    printf("Status: %d\n", (int)status);
  }
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
