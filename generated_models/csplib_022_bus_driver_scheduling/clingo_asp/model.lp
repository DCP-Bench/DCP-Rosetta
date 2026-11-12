% csplib_022_bus_driver_scheduling: a clingo model from DCP Rosetta.
%
% This problem requires finding an optimal schedule for bus drivers. Given a set of tasks (pieces of work) to cover and a large set of possible shifts, where each shift covers a subset of the tasks, we must select a subset of shifts that covers each piece of work exactly once. The goal is to cover all tasks while minimizing the total number of shifts used. The cost of each shift is considered equal.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
% Save this file as model.lp. Download `csplib_022_bus_driver_scheduling.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_022_bus_driver_scheduling.json
%   python -m clingo model.lp csplib_022_bus_driver_scheduling_1.lp

% Input: num_work(W): W pieces of work, numbered 0..W-1; num_shifts(S): S shifts, numbered 0..S-1;
% shifts(I, K, T): the K-th piece of work covered by shift I is the piece T (the lists have different lengths).

work(0..W-1) :- num_work(W).
shift(0..S-1) :- num_shifts(S).

% shift I covers piece of work T when T is in its list
covers(I, T) :- shifts(I, _, T).

% each shift is either selected or not
{ x(I, 1) } :- shift(I).
x(I, 0) :- shift(I), not x(I, 1).

% each piece of work is covered by exactly one selected shift
:- work(T), #count { I : x(I, 1), covers(I, T) } != 1.

% the number of shifts used is as small as possible (every shift costs the same)
#minimize { 1, I : x(I, 1) }.

#show x/2.
