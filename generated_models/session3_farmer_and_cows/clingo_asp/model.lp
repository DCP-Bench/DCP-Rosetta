% session3_farmer_and_cows: a clingo model from DCP Rosetta.
%
% A farmer has a number of cows, with each cow numbered from 1 up to the total number of cows. Each cow gives a quantity of milk equal to its number. The farmer has a number of sons and wants to distribute his cows to them according to a given distribution. The total quantity of milk produced should be the same for each son. How can he distribute the cows?
%
% Save this file as model.lp. Download `session3_farmer_and_cows.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session3_farmer_and_cows.json
%   python -m clingo model.lp session3_farmer_and_cows_1.lp
%
% Input: num_cows(N) holds the number N of cows; num_sons(S) the number S of sons; cows_per_son(S, K) the
% number K of cows that son S is to receive (indices are 0-based, as in the data).

cow(0..N-1) :- num_cows(N).
son(0..S-1) :- num_sons(S).

% each cow goes to exactly one son
1 { cow_assignments(I, S) : son(S) } 1 :- cow(I).

% each son receives the number of cows given for him
:- son(S), cows_per_son(S, K), #count { I : cow_assignments(I, S) } != K.

% the total milk of all the cows, where cow I gives I + 1 units of milk
max_milk(M) :- num_cows(N), M = N * (N + 1) / 2.

% the milk every son receives is one common amount T, chosen from the possible totals
1 { share(T) : T = 0..M } 1 :- max_milk(M).

% the milk of each son is that amount: the cows given to him give exactly T
:- son(S), share(T), #sum { I + 1, I : cow_assignments(I, S) } != T.

% the sons together receive all the milk, so T times the number of sons is the total (a redundant bound
% that only prunes the search)
:- share(T), num_sons(S), max_milk(M), T * S != M.

#show cow_assignments/2.
