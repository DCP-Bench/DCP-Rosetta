% just_forgotten: a clingo model from DCP Rosetta.
%
% Joe was furious when he forgot one of his bank account numbers. He remembered that it had all the digits
% from 0 to n-1 in some order, so he tried a number of sets without success. When Joe finally remembered his
% account number, he realised that in each set just a specific number of the digits were in their correct
% position and that, if one knew that, it was possible to work out his account number.
%
% Save this file as model.lp. Download `just_forgotten.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py just_forgotten.json
%   python -m clingo model.lp just_forgotten_1.lp
%
% Input: sets(S, I, D) holds that the S-th tried set (0-based) has the digit D at position I (indices are
% 0-based, as in the data); num_correct_digits(K) holds the number K of digits that are in their correct
% position in each set.

position(I) :- sets(_,I,_).

% x(I, D): the account number has the digit D at position I, and the digits are 0 to n-1, the same
% numbers as the positions
1 { x(I,D) : position(D) } 1 :- position(I).

% each digit is used exactly once
:- x(I1,D), x(I2,D), I1 < I2.

% each tried set has exactly K digits in the position they have in the account number
:- sets(S,_,_), num_correct_digits(K), K != #count { I : sets(S,I,D), x(I,D) }.

#show x/2.
