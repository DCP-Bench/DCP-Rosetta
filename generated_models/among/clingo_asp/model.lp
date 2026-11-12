% among: a clingo model from DCP Rosetta.
%
% Find an array x of n integers between 0 and 7, inclusive, such that exactly m of them take one of the values in v. The other elements may take any other value in that range.
%
% Save this file as model.lp. Download `among.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py among.json
%   python -m clingo model.lp among_1.lp

% Input: n(N): the array x has N entries; m(M): exactly M entries of x take a value in v;
% v(I, V): the I-th value of v is V (indices are 0-based, as in the data).

position(0..N-1) :- n(N).

% the integers of the statement are 0 to 7, inclusive
value(0..7).

% each entry of x takes exactly one value
1 { x(I, D) : value(D) } 1 :- position(I).

% an entry takes a value in v when its value is one of the values of v
in_v(I) :- x(I, V), v(_, V).

% exactly m entries of x take a value in v
:- m(M), #count { I : in_v(I) } != M.

#show x/2.
