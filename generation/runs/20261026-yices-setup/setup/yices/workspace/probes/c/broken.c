#include <stdio.h>
#include <stdlib.h>
#include <yices.h>
int main(int argc,char**argv){
 int init = argc>1;  if(init) yices_init();
 if(!init){ fprintf(stderr,"no init: about to call\n"); }
 type_t it=yices_int_type(); term_t x=yices_new_uninterpreted_term(it);
 term_t b=yices_new_uninterpreted_term(yices_bool_type());
 term_t bad=yices_add(x,b); /* type mismatch */
 printf("bad=%d code=%d\n",bad,yices_error_code()); char*s=yices_error_string(); printf("msg: %s\n",s); yices_free_string(s);
 term_t cascade=yices_arith_gt_atom(bad,yices_int32(0));
 printf("cascade=%d code=%d\n",cascade,yices_error_code());
 context_t*c=yices_new_context(NULL);
 int r=yices_assert_formula(c,cascade); printf("assert NULL_TERM rc=%d code=%d\n",r,yices_error_code());
 /* nonlinear in default context */
 yices_clear_error();
 term_t xx=yices_mul(x,x); r=yices_assert_formula(c,yices_arith_gt_atom(xx,yices_int32(10)));
 printf("nonlinear assert rc=%d code=%d\n",r,yices_error_code()); if(r<0){s=yices_error_string();printf("msg: %s\n",s);yices_free_string(s);}
 smt_status_t st=yices_check_context(c,NULL); printf("check st=%d\n",st);
 if(st==YICES_STATUS_ERROR){s=yices_error_string();printf("msg: %s\n",s);yices_free_string(s);}
 /* unchecked get_int64 */
 model_t*m=NULL; int64_t v=-777; if(st==YICES_STATUS_SAT){m=yices_get_model(c,1); int rc=yices_get_int64_value(m,b,&v); printf("get int of bool rc=%d v=%lld\n",rc,(long long)v);} 
 yices_exit(); return 0;}
