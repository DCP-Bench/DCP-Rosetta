% curious_set_of_integers: a clingo model from DCP Rosetta.
%
% The integers 1, 3, 8 and 120 form a set with a remarkable property: the product of any two of them is one
% less than a perfect square. Find a fifth number, larger than or equal to 0, that can be added to the set
% without destroying this property.
%
% Save this file as model.lp. Download `curious_set_of_integers.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py curious_set_of_integers.json
%   python -m clingo model.lp curious_set_of_integers_1.lp

% Input: n(N) holds the size N of the set once the new number is added; max_val(M) holds the largest
% value M to consider for the new number.

% the four given members of the set
given(1;3;8;120).

% the candidates for the new number are 0..M; a product with the new number plus one is at most 120*M+1,
% which is below (M+120)^2, so the squares R*R for R = 0..M+120 cover every product to test
value(0..M) :- max_val(M).
square(R*R) :- max_val(M), R = 0..M+120.

% the new number is one value from the candidates
1 { number(V) : value(V) } 1.

% the set has N members: the four given ones and the new number
:- n(N), #count { G : given(G) } != N - 1.

% the new number is not already a member of the set
:- number(V), given(V).

% the product of the new number and each given member is one less than a perfect square
:- number(V), given(G), not square(V*G+1).

#show number/1.
