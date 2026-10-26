#include <stdio.h>
#include <yices.h>
int main(void){ yices_init(); term_t x=yices_new_uninterpreted_term(yices_int_type());
 context_t*c=yices_new_context(NULL);
 yices_assert_formula(c,yices_arith_gt_atom(x,yices_int32(3))); yices_assert_formula(c,yices_arith_lt_atom(x,yices_int32(2)));
 smt_status_t st=yices_check_context(c,NULL); printf("status=%d\n",st);
 model_t*m=yices_get_model(c,1); printf("model after unsat: %p err=%d\n",(void*)m,yices_error_code());
 if(!m){char*s=yices_error_string();printf("%s\n",s);yices_free_string(s);}
 yices_exit(); return 0;}
