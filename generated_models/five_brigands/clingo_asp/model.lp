% five_brigands: a clingo model from DCP Rosetta.
%
% The five Spanish brigands, Alfonso, Benito, Carlos, Diego, and Esteban, were counting their spoils after a raid, when it was found that they had captured altogether exactly 200 doubloons. One of the band pointed out that if Alfonso had twelve times as much, Benito three times as much, Carlos the same amount, Diego half as much, and Esteban one-third as much, they would still have altogether just 200 doubloons. How many doubloons had each? Also, no brigand had less than one doubloon.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the amounts a brigand may have: at least one doubloon, and at most all the 200 doubloons
#const doubloons = 200.
val(1..doubloons).

% each brigand has exactly one amount: a for Alfonso, b for Benito, c for Carlos, d for Diego, e for Esteban
1 { a(V) : val(V) } 1.
1 { b(V) : val(V) } 1.
1 { c(V) : val(V) } 1.
1 { d(V) : val(V) } 1.
1 { e(V) : val(V) } 1.

% together they have exactly 200 doubloons
:- doubloons != #sum { V, a : a(V); V, b : b(V); V, c : c(V); V, d : d(V); V, e : e(V) }.

% after the change, the total is still 200: 12a + 3b + c + d/2 + e/3 = 200, multiplied by 6 to keep integers
:- doubloons * 6 != #sum { 72*V, a : a(V); 18*V, b : b(V); 6*V, c : c(V); 3*V, d : d(V); 2*V, e : e(V) }.

#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
