% chess_set: a clingo model from DCP Rosetta.
%
% A small joinery makes two different sizes of boxwood chess sets. The small set requires 3 hours of machining
% on a lathe, and the large set requires 2 hours. There are four lathes with skilled operators who each work a
% 40 hour week, so there are 160 lathe-hours per week. The small chess set requires 1 kg of boxwood, and the
% large set requires 3 kg. Boxwood is scarce and only 200 kg per week can be obtained. Each large chess set
% yields a profit of $20, and each small chess set a profit of $5. Decide how many sets of each kind should be
% made each week so as to maximize profit.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the number of small sets made in a week, from 0 to 100 (the lathe hours allow at most 53 of them, so the
% range is not limiting)
1 { small_set(N) : N = 0..100 } 1.

% the number of large sets made in a week, from 0 to 100 (the lathe hours allow at most 80 of them, so the
% range is not limiting)
1 { large_set(N) : N = 0..100 } 1.

% the boxwood used does not exceed the 200 kg available: 1 kg per small set and 3 kg per large set
:- small_set(S), large_set(L), S + 3 * L > 200.

% the lathe hours used do not exceed 160: 3 hours per small set and 2 hours per large set
:- small_set(S), large_set(L), 3 * S + 2 * L > 160.

% the profit: $5 per small set and $20 per large set, which is as large as possible
max_profit(5 * S + 20 * L) :- small_set(S), large_set(L).
#maximize { P : max_profit(P) }.

#show small_set/1.
#show large_set/1.
#show max_profit/1.
