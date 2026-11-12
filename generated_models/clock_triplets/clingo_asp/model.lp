% clock_triplets: a clingo model from DCP Rosetta.
%
% Rearrange the numbers on the face of a clock (1 to 12) so that no triplet of adjacent numbers has a sum higher
% than 21. This is the smallest value that the highest sum of a triplet can have.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% the twelve positions around the face, numbered 0 to 11 clockwise, and the numbers 1 to 12
position(0..11).
number(1..12).

% x(I, V): the position I holds the number V; each position holds exactly one number
1 { x(I, V) : number(V) } 1 :- position(I).

% each number is used once
:- x(I, V), x(J, V), I < J.

% three adjacent positions I, I+1 and I+2 (wrapping around the face) hold numbers whose sum is at most 21
:- position(I), x(I, A), x((I + 1) \ 12, B), x((I + 2) \ 12, C), A + B + C > 21.

#show x/2.
