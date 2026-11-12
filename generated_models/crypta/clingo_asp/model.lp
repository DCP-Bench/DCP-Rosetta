% crypta: a clingo model from DCP Rosetta.
%
% Cryptarithmetic puzzle, solve the operation:
%
%     B A I J J A J I I A H F C F E B B J E A
%   + D H F G A B C D I D B I F F A G F E J E
%   -----------------------------------------
%   = G J E G A C D D H F A F J B F I H E E F
%
% where all letters are distinct digits from 0 to 9, and the first letter of each number cannot be zero.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% col(K, X, Y, Z): in column K, counted from the right (0 is the units column), the first number has the letter X,
% the second number the letter Y, and the total the letter Z
col(0,a,e,f).   col(1,e,j,e).   col(2,j,e,e).   col(3,b,f,h).   col(4,b,g,i).
col(5,e,a,f).   col(6,f,f,b).   col(7,c,f,j).   col(8,f,i,f).   col(9,h,b,a).
col(10,a,d,f).  col(11,i,i,h).  col(12,i,d,d).  col(13,j,c,d).  col(14,a,b,c).
col(15,j,a,a).  col(16,j,g,g).  col(17,i,f,e).  col(18,a,h,j).  col(19,b,d,g).

letter(a). letter(b). letter(c). letter(d). letter(e). letter(f). letter(g). letter(h). letter(i). letter(j).

% each letter stands for exactly one digit from 0 to 9
1 { digit(L,V) : V = 0..9 } 1 :- letter(L).

% all letters are distinct digits
:- digit(L1,V), digit(L2,V), L1 < L2.

% the first letter of each number is not zero: the first letters are B, D and G
:- digit(b,0).
:- digit(d,0).
:- digit(g,0).

% carry(K) holds when the addition passes a carry of 1 from column K - 1 on to column K, which is the case
% for columns 1 to 19; there is no carry into the units column and none out of the last column
{ carry(K) : K = 1..19 }.

% in each column, the digit of the first number plus the digit of the second number plus the carry in
% equals the digit of the total plus 10 times the carry out
:- col(K,X,Y,Z), #sum { DX,x : digit(X,DX); DY,y : digit(Y,DY); 1,in : carry(K);
                        -DZ,z : digit(Z,DZ); -10,out : carry(K+1) } != 0.

% a(V), b(V), ...: the digit V that each letter stands for
a(V) :- digit(a,V).
b(V) :- digit(b,V).
c(V) :- digit(c,V).
d(V) :- digit(d,V).
e(V) :- digit(e,V).
f(V) :- digit(f,V).
g(V) :- digit(g,V).
h(V) :- digit(h,V).
i(V) :- digit(i,V).
j(V) :- digit(j,V).

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
