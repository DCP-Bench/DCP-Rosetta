% coin3_application: a clingo model from DCP Rosetta.
%
% Find the minimum number of coins that allows one to pay exactly any amount smaller than a given maximum amount using a given set of denominations.
%
% Save this file as model.lp. Download `coin3_application.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py coin3_application.json
%   python -m clingo model.lp coin3_application_1.lp
%
% Input: denominations(I, D) holds the denomination D of coin type I, and max_amount_to_pay(M) holds the
% maximum amount M (indices are 0-based, as in the data).

coin(I) :- denominations(I, _).
amount(1..M-1) :- max_amount_to_pay(M).

% the number of coins of each type is chosen; fewer than max_amount_to_pay coins of a type are ever needed,
% since an amount is paid with at most that many coins of it
1 { x(I, K) : K = 0..M-1 } 1 :- coin(I), max_amount_to_pay(M).

% each amount is paid with some number of coins of each type
1 { pay(A, I, K) : K = 0..A } 1 :- amount(A), coin(I).

% the coins paid for an amount do not exceed the coins of that type held
:- amount(A), pay(A, I, K), x(I, X), K > X.

% the coins paid for an amount add up to exactly that amount
:- amount(A), #sum { D*K, I : pay(A, I, K), denominations(I, D) } != A.

% minimize the total number of coins
#minimize { K, I : x(I, K) }.

#show x/2.
