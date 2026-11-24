% isbn: a clingo model from DCP Rosetta.
%
% ISBN-13 (International Standard Book Number) is a 13-digit number where the last digit is a check digit
% calculated from the first 12 digits. Multiply the first 12 digits alternately by 1 and 3 (starting with 1),
% sum the products, and the check digit is (10 - (sum % 10)) % 10. Given a list of 13 integers representing
% an ISBN-13, where -1 represents an unknown digit, find the values of the unknown digits such that the
% resulting number is a valid ISBN-13. An ISBN-13 must start with 978 or 979.
%
% Save this file as model.lp. Download `isbn.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py isbn.json
%   python -m clingo model.lp isbn_1.lp
%
% Input: isbn_init(I, V) holds the digit V at position I (indices are 0-based, as in the data), with
% V = -1 for an unknown digit.

position(I) :- isbn_init(I,_).
len(N) :- N = #count { I : position(I) }.

% isbn(I, D): the digit at position I is D
% each position holds exactly one digit from 0 to 9
1 { isbn(I,D) : D = 0..9 } 1 :- position(I).

% each known digit keeps its value
:- isbn_init(I,V), V != -1, not isbn(I,V).

% the ISBN starts with 978 or 979
:- not isbn(0,9).
:- not isbn(1,7).
:- not isbn(2,8), not isbn(2,9).

% weight(I, W): the first 12 digits are multiplied alternately by 1 and 3, starting with 1
weight(I,1) :- position(I), I \ 2 == 0.
weight(I,3) :- position(I), I \ 2 == 1.

% the sum of the first 12 digits multiplied by their weights
check_sum(S) :- S = #sum { D * W,I : isbn(I,D), weight(I,W), len(N), I < N - 1 }.

% the last digit is the check digit (10 - (sum % 10)) % 10
:- check_sum(S), len(N), not isbn(N - 1,(10 - S \ 10) \ 10).

#show isbn/2.
