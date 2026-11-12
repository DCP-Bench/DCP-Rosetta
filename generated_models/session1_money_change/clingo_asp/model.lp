% session1_money_change: a clingo model from DCP Rosetta.
%
% Alice has to give Bob some change. She has different types of coins of different values and she has a certain number of coins of each value available. How can the change be composed with the available coins minimizing the number of coins used?
%
% Save this file as model.lp. Download `session1_money_change.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session1_money_change.json
%   python -m clingo model.lp session1_money_change_1.lp

% Input: amount(A): the amount of change to give; types_of_coins(I,V): coin type I has value V;
% available_coins(I,N): N coins of type I are available (indices are 0-based).
coin(I) :- types_of_coins(I,_).

% for each coin type, the number of coins given is between 0 and the number available
1 { coin_counts(I,K) : K = 0..N } 1 :- coin(I), available_coins(I,N).

% the coins given add up to the amount
:- amount(A), #sum { K*V,I : coin_counts(I,K), types_of_coins(I,V) } != A.

% minimize the number of coins given
#minimize { K,I : coin_counts(I,K) }.

#show coin_counts/2.
