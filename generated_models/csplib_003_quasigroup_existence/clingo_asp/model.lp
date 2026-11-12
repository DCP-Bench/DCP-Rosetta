% csplib_003_quasigroup_existence: a clingo model from DCP Rosetta.
%
% An order m quasigroup is a Latin square of size m. That is, a m x m multiplication table in which each element
% occurs once in every row and column. A quasigroup can be specified by a set and a binary multiplication operator,
% * defined over this set. Quasigroup existence problems determine the existence or non-existence of quasigroups of a
% given size with additional properties. We define two new relations, *321 and *312 by a *321 b = c iff c * b = a and
% a *312 b = c iff b * c = a. QG3.m problems are order m quasigroups for which (a * b) * (b * a) = a. We only consider
% the QG3.m problem for this task.
%
% Save this file as model.lp. Download `csplib_003_quasigroup_existence.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_003_quasigroup_existence.json
%   python -m clingo model.lp csplib_003_quasigroup_existence_1.lp
%
% Input: m(M) holds the order M of the quasigroup, so the elements are the numbers 0 to M-1.

index(0..M-1) :- m(M).

% quasigroup(A, B, C): the product of A and B is C, the entry in row A and column B of the table.
% Every pair A, B has exactly one product.
1 { quasigroup(A,B,C) : index(C) } 1 :- index(A), index(B).

% each element occurs once in every row of the table
1 { quasigroup(A,B,C) : index(B) } 1 :- index(A), index(C).

% each element occurs once in every column of the table
1 { quasigroup(A,B,C) : index(A) } 1 :- index(B), index(C).

% (a * b) * (b * a) = a for all elements a and b: with x = a * b and y = b * a, the product of x and y is a
:- quasigroup(A,B,X), quasigroup(B,A,Y), not quasigroup(X,Y,A), index(A), index(B).

#show quasigroup/3.
