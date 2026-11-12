% csplib_067_quasigroup_completion: a clingo model from DCP Rosetta.
%
% An order m quasigroup is a Latin square of size m. That is, an m x m multiplication table in which each
% element from 1 to m occurs exactly once in every row and every column. This problem asks to complete a
% partially filled quasigroup, in which 0 marks an empty cell.
%
% Save this file as model.lp. Download `csplib_067_quasigroup_completion.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_067_quasigroup_completion.json
%   python -m clingo model.lp csplib_067_quasigroup_completion_1.lp

% Input: n(N): the order N of the quasigroup; start(R, C, V): the cell in row R and column C holds V,
% where V = 0 marks an empty cell (indices are 0-based, as in the data).

row(0..N-1) :- n(N).
column(0..N-1) :- n(N).
value(1..N) :- n(N).

% the filled cells keep the values they are given
given(R,C) :- start(R,C,V), V > 0.
puzzle(R,C,V) :- start(R,C,V), V > 0.

% each empty cell takes exactly one value
1 { puzzle(R,C,V) : value(V) } 1 :- row(R), column(C), not given(R,C).

% each value occurs exactly once in every row
:- puzzle(R,C1,V), puzzle(R,C2,V), C1 < C2.

% each value occurs exactly once in every column
:- puzzle(R1,C,V), puzzle(R2,C,V), R1 < R2.

#show puzzle/3.
