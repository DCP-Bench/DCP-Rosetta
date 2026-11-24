% csplib_019_magic_squares_and_sequences: a clingo model from DCP Rosetta.
%
% A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1} between 0 and n-1, such that for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence. As an example, 6, 2, 1, 0, 0, 0, 1, 0, 0, 0 is a magic sequence since 0 occurs 6 times in it, 1 occurs twice, etc.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
% Save this file as model.lp. Download `csplib_019_magic_squares_and_sequences.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_019_magic_squares_and_sequences.json
%   python -m clingo model.lp csplib_019_magic_squares_and_sequences_1.lp

% Input: n(N): the length N of the sequence (positions and values are 0-based).

pos(0..N-1) :- n(N).
val(0..N-1) :- n(N).

% each position holds exactly one value, between 0 and n-1
1 { x(I,V) : val(V) } 1 :- pos(I).

% the number I occurs exactly x_I times in the sequence
:- x(I,V), #count { J : x(J,I) } != V.

#show x/2.
