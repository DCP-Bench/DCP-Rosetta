#ifndef DCP_H
#define DCP_H
/* Header for Yices submissions in C. A submission starts with #include "dcp.h" and defines
 *
 *     void build(const cJSON *instance);
 *
 * It creates Yices terms, hands its constraints, its declared outputs and its objective to
 * the dcp_* functions below, and returns. The driver (driver.c) owns main(), yices_init(),
 * every context, the solving, the optimality proof and the enumeration. A failing dcp_*
 * call, or any Yices error it detects, ends the run with the status "error". */
#include <gmp.h> /* before yices.h: enables yices_get_mpz_value and yices_mpz */
#include <yices.h>
#include <cjson/cJSON.h>

void build(const cJSON *instance); /* defined by the submission */

/* ---- reading the instance ---- */
const cJSON *dcp_get(const cJSON *object, const char *key); /* a field; error when missing */
long long dcp_int(const cJSON *item);                       /* integral number (or Boolean as 0/1), |v| <= 2^53 */

/* ---- building the model ---- */
term_t dcp_chk(term_t t);          /* t, or an error naming the Yices failure when t is NULL_TERM */
void dcp_set_logic(const char *l); /* e.g. "QF_NIA" for nonlinear arithmetic; at most once */
void dcp_assert(term_t formula);   /* a Boolean term the solution must satisfy */

/* ---- declared outputs: a tree of leaves ---- */
cJSON *dcp_term(term_t t); /* a leaf: an integer or Boolean term */
void dcp_output(const char *name, cJSON *tree); /* tree: a leaf, or cJSON arrays of trees, any depth */

/* ---- objective: an integer term, at most one call ---- */
void dcp_minimize(term_t t);
void dcp_maximize(term_t t);

/* ---- failure ---- */
void dcp_fail(const char *format, ...) __attribute__((noreturn)); /* report status "error" with this message and stop */
#endif
