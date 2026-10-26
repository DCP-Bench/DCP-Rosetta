#include <stdio.h>
#include <yices.h>
int main(void){ yices_init(); term_t x=yices_new_uninterpreted_term(yices_int_type());
 context_t*c=yices_new_context(NULL); yices_assert_formula(c,yices_arith_geq_atom(x,yices_int32(1))); yices_assert_formula(c,yices_arith_leq_atom(x,yices_int32(5)));
 int n=0; while(yices_check_context(c,NULL)==YICES_STATUS_SAT && n<20){ model_t*m=yices_get_model(c,1); int64_t v; yices_get_int64_value(m,x,&v); printf("x=%lld\n",(long long)v); yices_free_model(m); n++; if(yices_assert_blocking_clause(c)<0){yices_print_error(stderr);break;} }
 printf("solutions found=%d (5 exist)\n",n); yices_exit(); return 0; }
