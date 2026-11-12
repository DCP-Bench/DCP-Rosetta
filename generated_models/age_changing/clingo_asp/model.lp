% age_changing: a clingo model from DCP Rosetta.
%
% If you start with my age, in years, and apply the four operations +2, /8, -3 and *7 in some order, then the final answer you get is my husband's age. If you start with his age and apply the same four operations in a different order, then you get my age. Both ages are between 16 and 120, and every intermediate result is a positive integer, so a division by 8 must be exact. What are our two ages?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

age(16..120).
op(0..3).         % 0: +2, 1: /8, 2: -3, 3: *7
position(0..3).   % the four steps of an order

% Values are positive integers. Starting from an age of at most 120, no chain of these four
% operations exceeds 5992, so 1..6000 holds every intermediate result.
value(1..6000).

% step(O,Old,New): operation O turns the value Old into New. Division by 8 is exact, so
% 8*New = Old, and the result must be a positive integer.
step(0,Old,Old+2) :- value(Old), Old+2 <= 6000.
step(1,Old,Old/8) :- value(Old), Old \ 8 == 0, Old/8 >= 1.
step(2,Old,Old-3) :- value(Old), Old-3 >= 1.
step(3,Old,Old*7) :- value(Old), Old*7 <= 6000.

% my age is A
1 { m(A) : age(A) } 1.

% perm1(K,O): the K-th operation from my age to my husband's age is O.
% perm2(K,O): the K-th operation from his age to mine is O.
% Each order uses every operation exactly once.
1 { perm1(K,O) : op(O) } 1 :- position(K).
1 { perm1(K,O) : position(K) } 1 :- op(O).
1 { perm2(K,O) : op(O) } 1 :- position(K).
1 { perm2(K,O) : position(K) } 1 :- op(O).

% the two orders are different: some position has different operations
differ :- perm1(K,O), not perm2(K,O).
:- not differ.

% hlist(K,V): the value after K operations applied to my age, in the first order
hlist(0,A) :- m(A).
hlist(K+1,New) :- hlist(K,Old), perm1(K,O), step(O,Old,New).

% h(V): my husband's age is V, the value after all four operations
h(V) :- hlist(4,V).
% my husband's age is between 16 and 120
:- h(V), not age(V).

% mlist(K,V): the value after K operations applied to my husband's age, in the second order
mlist(0,V) :- h(V).
mlist(K+1,New) :- mlist(K,Old), perm2(K,O), step(O,Old,New).
% the result of the second order is my age
:- m(A), not mlist(4,A).

% the orders are not outputs, and one pair of ages can come from several orders:
% project the enumeration onto the ages
#project m/1.
#project h/1.

#show m/1.
#show h/1.
