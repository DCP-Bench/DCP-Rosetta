/* Driver for Yices submissions (C API).
 *
 * The submission's build() creates terms and registers formulas, outputs and an objective.
 * This driver creates the context, solves, proves the optimum by tightening a strict bound,
 * enumerates solutions with no-goods over the declared outputs, and writes the runner
 * protocol: one "solution" record per solution, then one "status" record. The protocol goes
 * to a private copy of stdout; the process's own stdout is pointed at stderr, so nothing a
 * submission or Yices prints can reach the protocol.
 *
 * Nothing is emitted for an optimisation problem before the optimum is proven (UNSAT of
 * "objective better than the best found"). Further optimal solutions come from a fresh
 * context holding the same formulas plus "objective == optimum". */
#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include "dcp.h"

/* Exit code meaning "a status record was written"; run.py treats any other exit as a crash. */
#define STATUS_WRITTEN 79

static FILE *protocol;
static double t0, deadline;

static double now(void) {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void record(cJSON *rec) {
  char *text = cJSON_PrintUnformatted(rec);
  fputs(text, protocol);
  fputc('\n', protocol);
  fflush(protocol);
  free(text);
  cJSON_Delete(rec);
}

__attribute__((noreturn)) static void finish(const char *status, const char *detail) {
  cJSON *rec = cJSON_CreateObject();
  cJSON_AddStringToObject(rec, "type", "status");
  cJSON_AddStringToObject(rec, "status", status);
  cJSON_AddNumberToObject(rec, "solve_seconds", now() - t0);
  cJSON_AddStringToObject(rec, "detail", detail ? detail : "");
  record(rec);
  exit(STATUS_WRITTEN);
}

__attribute__((noreturn)) void dcp_fail(const char *format, ...) {
  char message[2048];
  va_list args;
  va_start(args, format);
  vsnprintf(message, sizeof message, format, args);
  va_end(args);
  finish("error", message);
}

/* "Yices: <message>" from the last Yices error. */
__attribute__((noreturn)) static void yices_fail(const char *what) {
  char *text = yices_error_string();
  dcp_fail("%s: %s", what, text ? text : "unknown Yices error");
}

term_t dcp_chk(term_t t) {
  if (t < 0) yices_fail("Yices rejected a term");
  return t;
}

/* ---- the model collected from build() ---- */
static term_t *formulas;
static size_t n_formulas, cap_formulas;
static char *logic;
static cJSON *outputs; /* name -> tree of {"$term": handle} leaves */
static term_t *leaves; /* the leaves, in tree order */
static int *leaf_is_bool;
static size_t n_leaves, cap_leaves;
static int has_objective, maximizing;
static term_t objective;

const cJSON *dcp_get(const cJSON *object, const char *key) {
  const cJSON *item = cJSON_IsObject(object) ? cJSON_GetObjectItemCaseSensitive(object, key) : NULL;
  if (!item) dcp_fail("The instance has no field '%s'", key);
  return item;
}

long long dcp_int(const cJSON *item) {
  if (!item) dcp_fail("dcp_int: no value");
  if (cJSON_IsBool(item)) return cJSON_IsTrue(item) ? 1 : 0;
  if (!cJSON_IsNumber(item)) dcp_fail("dcp_int: the value is not a number");
  double v = item->valuedouble;
  if (v != (double)(long long)v || v > 9007199254740992.0 || v < -9007199254740992.0)
    dcp_fail("dcp_int: %.17g is not an integer within +-2^53", v);
  return (long long)v;
}

void dcp_set_logic(const char *l) {
  if (logic) dcp_fail("dcp_set_logic was called twice");
  logic = strdup(l);
}

void dcp_assert(term_t f) {
  dcp_chk(f);
  if (n_formulas == cap_formulas) {
    cap_formulas = cap_formulas ? 2 * cap_formulas : 64;
    formulas = realloc(formulas, cap_formulas * sizeof *formulas);
  }
  formulas[n_formulas++] = f;
}

cJSON *dcp_term(term_t t) {
  dcp_chk(t);
  cJSON *leaf = cJSON_CreateObject();
  cJSON_AddNumberToObject(leaf, "$term", t);
  return leaf;
}

static void register_tree(const char *name, const cJSON *node) {
  if (cJSON_IsArray(node)) {
    const cJSON *child;
    cJSON_ArrayForEach(child, node) register_tree(name, child);
    return;
  }
  const cJSON *handle = cJSON_IsObject(node) ? cJSON_GetObjectItemCaseSensitive(node, "$term") : NULL;
  if (!handle) dcp_fail("Output '%s': every leaf must come from dcp_term and every container from cJSON_CreateArray", name);
  term_t t = (term_t)handle->valuedouble;
  int is_bool = yices_term_is_bool(t), is_int = yices_term_is_int(t);
  if (!is_bool && !is_int) dcp_fail("Output '%s': declared outputs must be integer or Boolean terms (a real, bit-vector or other term was given)", name);
  if (n_leaves == cap_leaves) {
    cap_leaves = cap_leaves ? 2 * cap_leaves : 64;
    leaves = realloc(leaves, cap_leaves * sizeof *leaves);
    leaf_is_bool = realloc(leaf_is_bool, cap_leaves * sizeof *leaf_is_bool);
  }
  leaves[n_leaves] = t;
  leaf_is_bool[n_leaves++] = is_bool;
}

void dcp_output(const char *name, cJSON *tree) {
  if (!outputs) outputs = cJSON_CreateObject();
  if (cJSON_HasObjectItem(outputs, name)) dcp_fail("Output '%s' was registered twice", name);
  register_tree(name, tree);
  cJSON_AddItemToObject(outputs, name, tree);
}

static void set_objective(term_t t, int maximize) {
  if (has_objective) dcp_fail("The objective was declared twice");
  dcp_chk(t);
  if (!yices_term_is_int(t)) dcp_fail("The objective must be an integer term");
  has_objective = 1;
  maximizing = maximize;
  objective = t;
}
void dcp_minimize(term_t t) { set_objective(t, 0); }
void dcp_maximize(term_t t) { set_objective(t, 1); }

/* ---- contexts and timed checks ---- */
static context_t *volatile running;
static void on_alarm(int sig) {
  (void)sig;
  context_t *c = running;
  if (c) yices_stop_search(c);
}

static context_t *new_context(void) {
  ctx_config_t *cfg = NULL;
  if (logic) {
    cfg = yices_new_config();
    if (yices_default_config_for_logic(cfg, logic) < 0) yices_fail("Unusable logic");
  }
  context_t *ctx = yices_new_context(cfg);
  if (!ctx) yices_fail("Cannot create a context");
  if (cfg) yices_free_config(cfg);
  for (size_t i = 0; i < n_formulas; i++)
    if (yices_assert_formula(ctx, formulas[i]) < 0) yices_fail("Cannot assert a formula");
  return ctx;
}

static void assert_term(context_t *ctx, term_t t) {
  if (yices_assert_formula(ctx, dcp_chk(t)) < 0) yices_fail("Cannot assert a formula");
}

/* One check within the deadline. *timed_out is set when the deadline ended it. */
static smt_status_t check(context_t *ctx, int *timed_out) {
  double left = deadline - now();
  *timed_out = 0;
  if (left <= 0.01) {
    *timed_out = 1;
    return YICES_STATUS_INTERRUPTED;
  }
  struct itimerval timer = {{0, 0}, {(time_t)left, (suseconds_t)((left - (time_t)left) * 1e6)}};
  struct itimerval off = {{0, 0}, {0, 0}};
  running = ctx;
  setitimer(ITIMER_REAL, &timer, NULL);
  smt_status_t st = yices_check_context(ctx, NULL);
  setitimer(ITIMER_REAL, &off, NULL);
  running = NULL;
  if (st == YICES_STATUS_INTERRUPTED || (st == YICES_STATUS_UNKNOWN && now() >= deadline - 0.05)) *timed_out = 1;
  return st;
}

/* ---- reading a solution ---- */
static mpz_t *leaf_int; /* the last read solution, in leaf order */
static int *leaf_bool;
static size_t leaf_cursor;

static cJSON *read_node(const cJSON *node, model_t *mdl) {
  if (cJSON_IsArray(node)) {
    cJSON *array = cJSON_CreateArray();
    const cJSON *child;
    cJSON_ArrayForEach(child, node) cJSON_AddItemToArray(array, read_node(child, mdl));
    return array;
  }
  size_t i = leaf_cursor++;
  if (leaf_is_bool[i]) {
    int32_t b;
    if (yices_get_bool_value(mdl, leaves[i], &b) < 0) yices_fail("Cannot read a Boolean output");
    leaf_bool[i] = b != 0;
    return cJSON_CreateBool(b != 0);
  }
  if (yices_get_mpz_value(mdl, leaves[i], leaf_int[i]) < 0) yices_fail("Cannot read an integer output");
  char *digits = mpz_get_str(NULL, 10, leaf_int[i]);
  cJSON *raw = cJSON_CreateRaw(digits);
  free(digits);
  return raw;
}

static cJSON *read_outputs(context_t *ctx) {
  model_t *mdl = yices_get_model(ctx, 1);
  if (!mdl) yices_fail("Cannot get a model");
  leaf_cursor = 0;
  cJSON *values = cJSON_CreateObject();
  const cJSON *item;
  cJSON_ArrayForEach(item, outputs) cJSON_AddItemToObject(values, item->string, read_node(item, mdl));
  yices_free_model(mdl);
  return values;
}

static void read_objective(context_t *ctx, mpz_t out) {
  model_t *mdl = yices_get_model(ctx, 1);
  if (!mdl) yices_fail("Cannot get a model");
  if (yices_get_mpz_value(mdl, objective, out) < 0) yices_fail("Cannot read the objective");
  yices_free_model(mdl);
}

static void emit_solution(cJSON *values) { /* takes ownership */
  cJSON *rec = cJSON_CreateObject();
  cJSON_AddStringToObject(rec, "type", "solution");
  cJSON_AddItemToObject(rec, "values", values);
  record(rec);
}

/* Reads a solution from a SAT context, or finishes the run: unsat, timeout, error. */
static const char *unknown_detail = "Yices returned unknown";

int main(void) {
  t0 = now();
  protocol = fdopen(dup(1), "w");
  if (!protocol) return 1;
  dup2(2, 1);

  size_t cap = 1 << 16, len = 0, got;
  char *text = malloc(cap + 1);
  while ((got = fread(text + len, 1, cap - len, stdin)) > 0) {
    len += got;
    if (len == cap) text = realloc(text, (cap *= 2) + 1);
  }
  text[len] = 0;
  cJSON *request = cJSON_Parse(text);
  if (!request) dcp_fail("The request is not valid JSON");
  const cJSON *tl = dcp_get(request, "execution_timeout");
  double budget = tl->valuedouble;
  long long limit = dcp_int(dcp_get(request, "solution_limit"));
  if (limit < 1) dcp_fail("solution_limit must be positive");
  deadline = t0 + (budget - 0.3 > 0.1 ? budget - 0.3 : 0.1);
  signal(SIGALRM, on_alarm);

  yices_init();
  yices_clear_error();
  build(dcp_get(request, "instance"));
  if (!outputs || n_leaves == 0) dcp_fail("build registered no outputs");
  leaf_int = malloc(n_leaves * sizeof *leaf_int);
  leaf_bool = calloc(n_leaves, sizeof *leaf_bool);
  for (size_t i = 0; i < n_leaves; i++) mpz_init(leaf_int[i]);

  context_t *ctx = new_context();
  int timed_out;
  cJSON *first = NULL; /* the last solution read, for limit 1 and for a satisfaction problem */
  mpz_t best;
  mpz_init(best);
  int found = 0;
  for (;;) {
    smt_status_t st = check(ctx, &timed_out);
    if (timed_out) finish("timeout", has_objective ? "Candidate optimum was not proven" : "");
    if (st == YICES_STATUS_UNSAT) {
      if (!found) finish("unsat", "");
      break;
    }
    if (st == YICES_STATUS_UNKNOWN) yices_fail(unknown_detail);
    if (st != YICES_STATUS_SAT) yices_fail("Yices check failed");
    found = 1;
    if (first) cJSON_Delete(first);
    first = read_outputs(ctx);
    if (!has_objective) break;
    read_objective(ctx, best);
    term_t bound = yices_mpz(best);
    assert_term(ctx, maximizing ? yices_arith_gt_atom(objective, bound) : yices_arith_lt_atom(objective, bound));
  }
  /* Here: a satisfaction problem with a solution in `first`, or the optimum proven. */
  if (limit == 1) {
    emit_solution(first);
    finish("limit", "");
  }
  if (has_objective) { /* a fresh context pinned to the optimum */
    cJSON_Delete(first);
    first = NULL;
    yices_free_context(ctx);
    ctx = new_context();
    assert_term(ctx, yices_arith_eq_atom(objective, yices_mpz(best)));
  }

  char **seen = NULL;
  size_t n_seen = 0;
  long long count = 0;
  term_t *differs = malloc(n_leaves * sizeof *differs);
  for (;;) {
    cJSON *values = first;
    first = NULL;
    if (!values) {
      smt_status_t st = check(ctx, &timed_out);
      if (timed_out) finish("timeout", "");
      if (st == YICES_STATUS_UNSAT) {
        if (!count) dcp_fail("The optimum could not be reproduced for enumeration");
        finish("complete", "");
      }
      if (st == YICES_STATUS_UNKNOWN) yices_fail(unknown_detail);
      if (st != YICES_STATUS_SAT) yices_fail("Yices check failed");
      values = read_outputs(ctx);
    }
    char *key = cJSON_PrintUnformatted(values);
    int fresh = 1;
    for (size_t i = 0; i < n_seen; i++)
      if (!strcmp(seen[i], key)) fresh = 0;
    if (fresh) {
      seen = realloc(seen, (n_seen + 1) * sizeof *seen);
      seen[n_seen++] = key;
      emit_solution(values);
      if (++count >= limit) finish("limit", "");
    } else {
      free(key);
      cJSON_Delete(values);
    }
    /* No-good over the declared outputs only. */
    for (size_t i = 0; i < n_leaves; i++) {
      if (leaf_is_bool[i]) differs[i] = leaf_bool[i] ? yices_not(leaves[i]) : leaves[i];
      else differs[i] = yices_arith_neq_atom(leaves[i], yices_mpz(leaf_int[i]));
      dcp_chk(differs[i]);
    }
    assert_term(ctx, yices_or((uint32_t)n_leaves, differs));
  }
}
