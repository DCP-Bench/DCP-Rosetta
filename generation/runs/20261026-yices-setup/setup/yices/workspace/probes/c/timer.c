#include <stdio.h>
#include <signal.h>
#include <sys/time.h>
#include <yices.h>
static context_t *cur;
static void on_alarm(int sig){ (void)sig; yices_stop_search(cur); }
int main(void){ yices_init(); type_t it=yices_int_type(); enum{N=14}; term_t x[N];
 context_t*c=yices_new_context(NULL); cur=c;
 for(int i=0;i<N;i++){x[i]=yices_new_uninterpreted_term(it); yices_assert_formula(c,yices_arith_geq_atom(x[i],yices_int32(0))); yices_assert_formula(c,yices_arith_leq_atom(x[i],yices_int32(N*N)));}
 /* hard: all-different sums via pairwise differences distinct (Golomb-like) */
 term_t d[N*N]; int k=0; for(int i=0;i<N;i++)for(int j=i+1;j<N;j++) d[k++]=yices_sub(x[j],x[i]);
 for(int i=0;i<N-1;i++) yices_assert_formula(c,yices_arith_lt_atom(x[i],x[i+1]));
 yices_assert_formula(c,yices_distinct(k,d));
 yices_assert_formula(c,yices_arith_lt_atom(x[N-1],yices_int32(N*N/2)));
 signal(SIGALRM,on_alarm); struct itimerval t={{0,0},{1,0}}; setitimer(ITIMER_REAL,&t,NULL);
 smt_status_t st=yices_check_context(c,NULL); struct itimerval z={{0,0},{0,0}}; setitimer(ITIMER_REAL,&z,NULL);
 printf("status=%d (INTERRUPTED=%d)\n",st,YICES_STATUS_INTERRUPTED);
 if(st==YICES_STATUS_INTERRUPTED){ printf("model: %p\n",(void*)yices_get_model(c,1)); yices_clear_error();
   printf("check again=%d\n",yices_check_context(c,NULL)); yices_clear_error();
   yices_reset_context(c); printf("after reset status=%d\n",yices_context_status(c)); }
 yices_exit(); return 0; }
