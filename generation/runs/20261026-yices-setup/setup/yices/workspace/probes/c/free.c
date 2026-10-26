#include <stdio.h>
#include <yices.h>
int main(void){ yices_init(); type_t it=yices_int_type();
 term_t x=yices_new_uninterpreted_term(it), y=yices_new_uninterpreted_term(it), b=yices_new_uninterpreted_term(yices_bool_type());
 context_t*c=yices_new_context(NULL); yices_assert_formula(c,yices_arith_gt_atom(x,yices_int32(0)));
 yices_check_context(c,NULL); model_t*m=yices_get_model(c,1); int64_t v=-5; int rc;
 rc=yices_get_int64_value(m,x,&v); printf("x rc=%d v=%lld\n",rc,(long long)v);
 v=-5; rc=yices_get_int64_value(m,y,&v); printf("free y rc=%d v=%lld\n",rc,(long long)v);
 int32_t bv=-9; rc=yices_get_bool_value(m,b,&bv); printf("free b rc=%d v=%d\n",rc,bv);
 yices_free_model(m); yices_exit(); return 0; }
