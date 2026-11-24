% dudeney_numbers: a clingo model from DCP Rosetta.
%
% A Dudeney Number is a positive integer that is a perfect cube such that the sum of its digits is equal to the cube root of the number. Such a number must also be larger than 1 and have at most n digits.
%
% Save this file as model.lp. Download `dudeney_numbers.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py dudeney_numbers.json
%   python -m clingo model.lp dudeney_numbers_1.lp

% Input: n(N) holds the most digits N that the number may have.

% the places of the number, from the units (place 0) up to the most significant digit
place(0..N-1) :- n(N).

% the cube root R is chosen from 1..9N, since the digits are at most 9 each and there are N of them
1 { root(R) : R = 1..9*N } 1 :- n(N).

% the number is larger than 1
:- root(R), R < 2.

% the cube has at most n digits
:- root(R), n(N), R*R*R >= 10**N.

% the digit at each place of the cube: the cube divided by 10 to the power of the place, modulo 10
digit(R, K, (R*R*R / 10**K) \ 10) :- root(R), place(K).

% the digits of the cube add up to the cube root
:- root(R), #sum { D, K : digit(R, K, D) } != R.

% the Dudeney number is the cube of the root
number(R*R*R) :- root(R).

#show number/1.
