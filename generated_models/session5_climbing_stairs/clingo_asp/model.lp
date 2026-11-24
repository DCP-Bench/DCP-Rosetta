% session5_climbing_stairs: a clingo model from DCP Rosetta.
%
% We want to climb a stair of n steps with a number of steps at a time, within a given range [m1, m2]. For example a stair of 4 steps with m1 = 1, and m2 = 2 can be climbed with a sequence of four one-step moves or with two two-steps moves. Find a way to climb a stair of n steps, i.e. you can take only m1 to m2 steps at a time.
%
% Save this file as model.lp. Download `session5_climbing_stairs.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session5_climbing_stairs.json
%   python -m clingo model.lp session5_climbing_stairs_1.lp
%
% Input: n(N) holds the number N of steps of the stair; m1(A) and m2(B) hold the smallest number A and the
% largest number B of steps that can be taken in one move.

% there are n moves, numbered from 0; after the top is reached, the remaining moves take 0 steps
move(0..N-1) :- n(N).

% the numbers of steps a move can take: 0, or any number from m1 to m2
step_count(0).
step_count(A..B) :- m1(A), m2(B).

% each move takes one of these numbers of steps
{ steps(K, V) : step_count(V) } = 1 :- move(K).

% the steps taken add up to the number of steps of the stair
:- n(N), #sum { V, K : steps(K, V) } != N.

% once a move takes no steps, the top has been reached and every later move takes no steps
:- steps(K, 0), steps(K2, V), K < K2, V > 0.

#show steps/2.
