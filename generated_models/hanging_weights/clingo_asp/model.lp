% hanging_weights: a clingo model from DCP Rosetta.
%
% The diagram shows a set of weights (A-M) hanging from a system of bars. The weights have different
% integer values between 1 and 13, and the goal is to find the value of each weight so that the diagram
% balances as shown. Each three characters along a bar are one unit of distance. The weights on either
% side of a pivot point must be equal when weighted by their distance from the pivot, and a bar hanging
% beneath another contributes its total weight as though it were a single weight.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

object(a;b;c;d;e;f;g;h;i;j;k;l;m).

% each weight has exactly one value from 1 to 13
1 { w(O,V) : V = 1..13 } 1 :- object(O).

% the weights have different values
:- w(O1,V), w(O2,V), O1 < O2.

% hangs(B, O, U): the weight O hangs from the bar B at U units from its pivot, U > 0 to the left
% and U < 0 to the right; a bar hanging beneath another is listed with the weights on it, at the
% same distance as the bar

% the bar A-B: A hangs 4 units left of the pivot and B 1 unit right, so 4*A = B
hangs(ab,a,4). hangs(ab,b,-1).

% the bar C-D: C hangs 5 units left of the pivot and D 1 unit right, so 5*C = D
hangs(cd,c,5). hangs(cd,d,-1).

% the bar E-F: E hangs 3 units left of the pivot and F 2 units right, so 3*E = 2*F
hangs(ef,e,3). hangs(ef,f,-2).

% the bar G, hung beneath the bar C-D: G hangs 3 units left of the pivot and the bar C-D 2 units right,
% so 3*G = 2*(C+D)
hangs(gcd,g,3). hangs(gcd,c,-2). hangs(gcd,d,-2).

% the bar with J and K: J hangs 2 units left of the pivot, the bar A-B 3 units left, K 1 unit right and
% the bar G-C-D 2 units right
hangs(jk,j,2). hangs(jk,a,3). hangs(jk,b,3).
hangs(jk,k,-1). hangs(jk,g,-2). hangs(jk,c,-2). hangs(jk,d,-2).

% the bar H-I, hung beneath the bar E-F: H hangs 3 units left of the pivot, the bar E-F 2 units right and
% I 3 units right, so 3*H = 2*(E+F) + 3*I
hangs(hi,h,3). hangs(hi,e,-2). hangs(hi,f,-2). hangs(hi,i,-3).

% the bar with L and M, whose left end carries the bar H-I-E-F: that bar hangs 1 unit left of the pivot,
% L 1 unit right and M 4 units right, so H+I+E+F = L + 4*M
hangs(lm,h,1). hangs(lm,i,1). hangs(lm,e,1). hangs(lm,f,1).
hangs(lm,l,-1). hangs(lm,m,-4).

% the top bar: its left arm, the bar L-M, hangs 4 units left of the pivot and its right arm, the bar
% carrying J, K, G, A, B, C and D, 3 units right, so 4*(L+M+H+I+E+F) = 3*(J+K+G+A+B+C+D)
hangs(top,l,4). hangs(top,m,4). hangs(top,h,4). hangs(top,i,4). hangs(top,e,4). hangs(top,f,4).
hangs(top,j,-3). hangs(top,k,-3). hangs(top,g,-3). hangs(top,a,-3). hangs(top,b,-3).
hangs(top,c,-3). hangs(top,d,-3).

bar(ab;cd;ef;gcd;jk;hi;lm;top).

% every bar balances: the distances times the weights on it add up to zero
:- bar(B), #sum { U*V,O : hangs(B,O,U), w(O,V) } != 0.

% the answer: the value of each weight
a(V) :- w(a,V).
b(V) :- w(b,V).
c(V) :- w(c,V).
d(V) :- w(d,V).
e(V) :- w(e,V).
f(V) :- w(f,V).
g(V) :- w(g,V).
h(V) :- w(h,V).
i(V) :- w(i,V).
j(V) :- w(j,V).
k(V) :- w(k,V).
l(V) :- w(l,V).
m(V) :- w(m,V).

#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
#show f/1.
#show g/1.
#show h/1.
#show i/1.
#show j/1.
#show k/1.
#show l/1.
#show m/1.
