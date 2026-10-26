#include <stdio.h>
#include <yices.h>
static void err(const char*w){ char*s=yices_error_string(); printf("%s: code=%d msg=%s\n",w,(int)yices_error_code(),s); yices_free_string(s); yices_clear_error(); }
int main(void){
 yices_init();
 printf("version=%s mcsat=%d\n", yices_version, yices_has_mcsat());
 type_t it=yices_int_type(); term_t x=yices_new_uninterpreted_term(it), y=yices_new_uninterpreted_term(it), z=yices_new_uninterpreted_term(it);
 /* R2 output term in no assertion */
 context_t*c=yices_new_context(NULL);
 yices_assert_formula(c,yices_arith_gt_atom(x,yices_int32(0)));
 yices_check_context(c,NULL); model_t*m=yices_get_model(c,1); int64_t v=-5;
 printf("free y rc=%d v=%lld\n",yices_get_int64_value(m,y,&v),(long long)v); if(yices_error_code()) err("free y"); yices_free_model(m);
 m=yices_get_model(c,1); v=-5; printf("keep_subst=1 x rc=%d v=%lld\n",yices_get_int64_value(m,x,&v),(long long)v); yices_free_model(m);
 /* assert after SAT, push/pop tightening */
 printf("assert after SAT rc=%d\n", yices_assert_formula(c,yices_arith_lt_atom(x,yices_int32(3)))); if(yices_error_code()) err("assert after sat");
 yices_push(c); yices_assert_formula(c,yices_arith_gt_atom(x,yices_int32(10)));
 printf("check1=%d\n",yices_check_context(c,NULL)); 
 yices_assert_formula(c,yices_arith_lt_atom(x,yices_int32(0)));
 printf("assert after unsat rc=%d\n",0); 
 printf("check2=%d\n",yices_check_context(c,NULL)); if(yices_error_code()) err("check2");
 printf("pop rc=%d\n",yices_pop(c)); printf("check3=%d\n",yices_check_context(c,NULL));
 /* distinct */
 term_t a[1]={x}; term_t d=yices_distinct(1,a); printf("distinct1=%d\n",d); if(d<0) err("distinct 1");
 d=yices_distinct(0,a); printf("distinct0=%d\n",d); if(d<0) err("distinct 0");
 /* div mod */
 term_t m7=yices_int32(-7), t2=yices_int32(2);
 term_t dv=yices_idiv(m7,t2), md=yices_imod(m7,t2);
 context_t*c2=yices_new_context(NULL); yices_assert_formula(c2,yices_arith_eq_atom(z,dv)); yices_assert_formula(c2,yices_arith_eq_atom(y,md));
 yices_check_context(c2,NULL); m=yices_get_model(c2,1); int64_t q,r; yices_get_int64_value(m,z,&q); yices_get_int64_value(m,y,&r); printf("-7 div 2=%lld mod=%lld\n",(long long)q,(long long)r); yices_free_model(m);
 /* new_variable misuse */
 term_t var=yices_new_variable(it); context_t*c3=yices_new_context(NULL);
 int rc=yices_assert_formula(c3,yices_arith_gt_atom(var,yices_int32(0))); printf("assert free-variable rc=%d\n",rc); if(rc<0) err("variable");
 /* wide */
 context_t*c4=yices_new_context(NULL); term_t big=yices_parse_term("100000000000000000000"); yices_assert_formula(c4,yices_arith_eq_atom(x,big));
 yices_check_context(c4,NULL); m=yices_get_model(c4,1); v=0; rc=yices_get_int64_value(m,x,&v); printf("wide rc=%d\n",rc); if(rc<0) err("wide"); 
 int32_t v32; yices_get_int32_value(m,y,&v32); yices_free_model(m);
 /* bool reading and ite, product of vars default ctx */
 term_t p=yices_mul(x,y); rc=yices_assert_formula(c3,yices_arith_gt_atom(p,yices_int32(3))); printf("nonlin rc=%d\n",rc);if(rc<0)err("nonlin");
 /* MCSAT */
 ctx_config_t*cfg=yices_new_config(); printf("cfg rc=%d\n",yices_default_config_for_logic(cfg,"QF_NIA")); 
 context_t*c5=yices_new_context(cfg); yices_free_config(cfg);
 yices_assert_formula(c5,yices_arith_eq_atom(yices_mul(x,y),yices_int32(12))); yices_assert_formula(c5,yices_arith_gt_atom(x,yices_int32(2))); yices_assert_formula(c5,yices_arith_gt_atom(y,x));
 printf("nia check=%d\n",yices_check_context(c5,NULL)); m=yices_get_model(c5,1); yices_get_int64_value(m,x,&v); yices_get_int64_value(m,y,&q); printf("x=%lld y=%lld\n",(long long)v,(long long)q);
 /* push/pop + assert after sat under mcsat */
 printf("mcsat assert after sat rc=%d\n",yices_assert_formula(c5,yices_arith_lt_atom(x,yices_int32(100)))); if(yices_error_code())err("mcsat assert after sat");
 printf("mcsat check=%d\n",yices_check_context(c5,NULL));
 /* stop_search on idle */
 yices_stop_search(c5); printf("stop idle ok status=%d\n",yices_context_status(c5));
 yices_exit(); return 0; }
