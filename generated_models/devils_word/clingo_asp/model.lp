% devils_word: a clingo model from DCP Rosetta.
%
% Given an array of integers, insert a plus or a minus sign before each integer so that the signed numbers
% add up to a given total (666 for the devil's word).
%
% Save this file as model.lp. Download `devils_word.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py devils_word.json
%   python -m clingo model.lp devils_word_1.lp

% Input: arr(I, A): the I-th number of the array is A (indices 0-based); total(T): the total T to reach.

% each number is either added (plus(I)) or subtracted
{ plus(I) } :- arr(I,_).

% signed(I, S): the I-th number with its sign applied, S
signed(I,A) :- plus(I), arr(I,A).
signed(I,-A) :- arr(I,A), not plus(I).

% the signed numbers add up to the total
:- total(T), #sum { S,I : signed(I,S) } != T.

result(I,S) :- signed(I,S).

#show result/2.
