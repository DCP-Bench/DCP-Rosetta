#include <stdio.h>
#include <string.h>
#include <yices.h>
/* items weights {3,4,5,2} values {4,5,6,3}, cap 9; build via function; MODE=max|min|allopt */
#define N 4
static const int W[N]={3,4,5,2}, V[N]={4,5,6,3};
static term_t x[N], obj;
static context_t *build(void){
  context_t *ctx = yices_new_context(NULL);
  term_t ws[N], vs[N];
  for(int i=0;i<N;i++){ yices_assert_formula(ctx, yices_arith_geq_atom(x[i],yices_int32(0))); yices_assert_formula(ctx, yices_arith_leq_atom(x[i],yices_int32(1)));
    ws[i]=yices_mul(yices_int32(W[i]),x[i]); vs[i]=yices_mul(yices_int32(V[i]),x[i]); }
  yices_assert_formula(ctx, yices_arith_leq_atom(yices_sum(N,ws), yices_int32(9)));
  return ctx;
}
int main(int argc,char**argv){
  int maxi = strcmp(argv[1],"min")!=0;
  yices_init();
  term_t vs[N];
  for(int i=0;i<N;i++) x[i]=yices_new_uninterpreted_term(yices_int_type());
  for(int i=0;i<N;i++) vs[i]=yices_mul(yices_int32(V[i]),x[i]);
  obj=yices_sum(N,vs);
  context_t *ctx=build(); long best=0; int have=0; smt_status_t st;
  while((st=yices_check_context(ctx,NULL))==YICES_STATUS_SAT){
    model_t*m=yices_get_model(ctx,1); int64_t o; yices_get_int64_value(m,obj,&o); yices_free_model(m);
    best=o; have=1; printf("found %ld\n",best);
    if(yices_assert_formula(ctx, maxi?yices_arith_gt_atom(obj,yices_int64(best)):yices_arith_lt_atom(obj,yices_int64(best)))<0){yices_print_error(stderr);return 1;}
  }
  printf("last status=%d have=%d best=%ld\n",st,have,best);
  yices_free_context(ctx);
  if(argc>2){ /* enumerate all optimal in fresh context */
    ctx=build(); yices_assert_formula(ctx, yices_arith_eq_atom(obj,yices_int64(best))); int n=0;
    while(yices_check_context(ctx,NULL)==YICES_STATUS_SAT){ model_t*m=yices_get_model(ctx,1); term_t ng[N]; printf("opt:");
      for(int i=0;i<N;i++){int64_t v;yices_get_int64_value(m,x[i],&v);printf(" %lld",(long long)v);ng[i]=yices_arith_neq_atom(x[i],yices_int64(v));}
      printf("\n"); n++; yices_free_model(m); yices_assert_formula(ctx,yices_or(N,ng)); }
    printf("n_opt=%d\n",n); yices_free_context(ctx);
  }
  yices_exit(); return 0;
}
