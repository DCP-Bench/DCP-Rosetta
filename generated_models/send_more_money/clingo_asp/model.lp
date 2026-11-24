% send_more_money: a clingo model from DCP Rosetta.
%
% The "Send More Money" puzzle is a classic cryptarithmetic problem where each letter represents a unique digit. The goal is to assign digits to the letters such that the following equation holds true:
%
%    SEND
%  + MORE
%  ------
%   MONEY
%
% Each letter must be assigned a unique digit from 0 to 9, and the first letter of each word cannot be zero.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

letter(s;e;n;d;m;o;r;y).

% each letter is assigned exactly one digit from 0 to 9
1 { digit(L,V) : V = 0..9 } 1 :- letter(L).

% each digit is assigned to at most one letter, so the letters have unique digits
:- digit(L1,V), digit(L2,V), L1 < L2.

% the first letter of each word is not zero: S of SEND, M of MORE and MONEY
:- digit(s,0).
:- digit(m,0).

% SEND + MORE = MONEY, with each word read as a number: SEND + MORE - MONEY = 0. The second
% tuple element only keeps equal terms (such as the two E's) apart.
:- #sum { 1000*V,send_s : digit(s,V);  100*V,send_e : digit(e,V);  10*V,send_n : digit(n,V);  V,send_d : digit(d,V);
          1000*V,more_m : digit(m,V);  100*V,more_o : digit(o,V);  10*V,more_r : digit(r,V);  V,more_e : digit(e,V);
          -10000*V,money_m : digit(m,V);  -1000*V,money_o : digit(o,V);  -100*V,money_n : digit(n,V);
          -10*V,money_e : digit(e,V);  -V,money_y : digit(y,V) } != 0.

% the digit of each letter, as one atom per letter: s(V), e(V), ...
s(V) :- digit(s,V).
e(V) :- digit(e,V).
n(V) :- digit(n,V).
d(V) :- digit(d,V).
m(V) :- digit(m,V).
o(V) :- digit(o,V).
r(V) :- digit(r,V).
y(V) :- digit(y,V).

#show s/1.
#show e/1.
#show n/1.
#show d/1.
#show m/1.
#show o/1.
#show r/1.
#show y/1.
