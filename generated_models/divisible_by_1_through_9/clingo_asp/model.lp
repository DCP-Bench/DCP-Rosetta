% divisible_by_1_through_9: a clingo model from DCP Rosetta.
%
% Find a 10 digit number that uses each of the digits 0 to 9 exactly once and where the number formed by the
% first n digits of the number is divisible by n, for every n from 1 to 10. Read the digits from left to right:
% in the number abcd, the number a is divisible by 1, ab by 2, abc by 3 and abcd by 4.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% digits(P, D): the digit at position P, counted from the left from 0, is D
position(0..9).
digit(0..9).

% each position holds exactly one digit
1 { digits(P,D) : digit(D) } 1 :- position(P).

% each of the digits 0 to 9 is used exactly once
:- digit(D), #count { P : digits(P,D) } != 1.

% the number has ten digits, so its first digit is not 0
:- digits(0,0).

% the number formed by the first N digits is divisible by N. That number can be larger than clingo's integers,
% so each place value 10**(N-1-P) is replaced by its remainder modulo N, which leaves the remainder of the
% sum modulo N unchanged
divisor(1..10).
:- divisor(N), S = #sum { D * ((10 ** (N-1-P)) \ N), P : digits(P,D), P < N }, S \ N != 0.

#show digits/2.
