% csplib_041_n_fractions: a clingo model from DCP Rosetta.
%
% Find distinct non-zero digits such that the following equation holds: A / BC + D / EF + G / HI = 1
% Here, BC, EF, and HI are two-digit numbers formed by B and C, E and F, and H and I, respectively.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

digit(1..9).

% each letter stands for exactly one non-zero digit
1 { a(X) : digit(X) } 1.
1 { b(X) : digit(X) } 1.
1 { c(X) : digit(X) } 1.
1 { d(X) : digit(X) } 1.
1 { e(X) : digit(X) } 1.
1 { f(X) : digit(X) } 1.
1 { g(X) : digit(X) } 1.
1 { h(X) : digit(X) } 1.
1 { i(X) : digit(X) } 1.

% the digits are distinct: no digit stands for more than one letter
:- digit(X), #count { 1,a : a(X); 1,b : b(X); 1,c : c(X); 1,d : d(X); 1,e : e(X);
                      1,f : f(X); 1,g : g(X); 1,h : h(X); 1,i : i(X) } > 1.

% A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI, where BC = 10*B + C, EF = 10*E + F and HI = 10*H + I:
%   A * EF * HI + D * BC * HI + G * BC * EF - BC * EF * HI = 0
% Each product is expanded into terms of three digits, so that every term is a sum over chosen digits.
:- #sum {
     100*A*E*H,1,A,E,H : a(A), e(E), h(H);
      10*A*E*I,2,A,E,I : a(A), e(E), i(I);
      10*A*F*H,3,A,F,H : a(A), f(F), h(H);
         A*F*I,4,A,F,I : a(A), f(F), i(I);
     100*D*B*H,5,D,B,H : d(D), b(B), h(H);
      10*D*B*I,6,D,B,I : d(D), b(B), i(I);
      10*D*C*H,7,D,C,H : d(D), c(C), h(H);
         D*C*I,8,D,C,I : d(D), c(C), i(I);
     100*G*B*E,9,G,B,E : g(G), b(B), e(E);
      10*G*B*F,10,G,B,F : g(G), b(B), f(F);
      10*G*C*E,11,G,C,E : g(G), c(C), e(E);
         G*C*F,12,G,C,F : g(G), c(C), f(F);
    -1000*B*E*H,13,B,E,H : b(B), e(E), h(H);
     -100*B*E*I,14,B,E,I : b(B), e(E), i(I);
     -100*B*F*H,15,B,F,H : b(B), f(F), h(H);
      -10*B*F*I,16,B,F,I : b(B), f(F), i(I);
     -100*C*E*H,17,C,E,H : c(C), e(E), h(H);
      -10*C*E*I,18,C,E,I : c(C), e(E), i(I);
      -10*C*F*H,19,C,F,H : c(C), f(F), h(H);
         -C*F*I,20,C,F,I : c(C), f(F), i(I)
   } != 0.

#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
#show f/1.
#show g/1.
#show h/1.
#show i/1.
