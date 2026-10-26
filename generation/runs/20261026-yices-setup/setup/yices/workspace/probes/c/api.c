#include <stdio.h>
#include <gmp.h>
#include <yices.h>
int main(void){ yices_init();
 term_t x=yices_new_uninterpreted_term(yices_int_type()), p=yices_new_uninterpreted_term(yices_bool_type()), q=yices_new_uninterpreted_term(yices_bool_type());
 term_t f[]={ yices_implies(p,q), yices_iff(p,q), yices_xor2(p,q), yices_and2(p,q), yices_or2(p,q), yices_not(p),
   yices_eq(x,yices_int32(3)), yices_neq(x,yices_int32(4)), yices_ite(p,x,yices_int32(0)), yices_neg(x), yices_abs(x), yices_square(x),
   yices_arith_geq0_atom(x), yices_true(), yices_false(), yices_product(1,&x), yices_power(x,2), yices_zero(), yices_mpz((mpz_t){0}) };
 for(unsigned i=0;i<sizeof f/sizeof*f;i++) printf("%d ",f[i]); printf("\n");
 context_t*c=yices_new_context(NULL); yices_assert_formula(c,yices_eq(x,yices_parse_term("123456789012345678901234567890"))); yices_check_context(c,NULL);
 model_t*m=yices_get_model(c,1); mpz_t z; mpz_init(z); int rc=yices_get_mpz_value(m,x,z); gmp_printf("rc=%d %Zd\n",rc,z);
 int32_t b; yices_get_bool_value(m,yices_true(),&b); printf("true=%d\n",b);
 printf("simple eq of int/bool: %d\n", yices_eq(x,p)); char*s=yices_error_string(); printf("%s\n",s);
 term_t named=yices_new_uninterpreted_term(yices_int_type()); yices_set_term_name(named,"v"); printf("name=%s\n",yices_get_term_name(named));
 yices_pp_term(stdout,yices_arith_gt_atom(x,yices_int32(1)),80,1,0);
 yices_exit(); return 0;}
