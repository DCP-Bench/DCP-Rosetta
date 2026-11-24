% netasgn: a clingo model from DCP Rosetta.
%
% Consider a project assignment problem. Given a set of people `People` and a set of projects `Projects`. Each person `i` has a certain number of available hours `Supply_{i}` and each project `j` requires a certain number of hours `Demand_{j}`. The cost per hour of work for person `i` on project `j` is `Cost_{i, j}`. Each person `i` can contribute to project `j` up to a maximum limit `Limit_{i, j}`. The problem aims to minimize the total cost of assigning people to projects. It is constrained that the total number of hours assigned from each person `i` equals its supply and the total number of hours assigned to each project `j` equals its demand.
%
% Save this file as model.lp. Download `netasgn.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py netasgn.json
%   python -m clingo model.lp netasgn_1.lp
%
% Input: supply(I, S) the hours S available from person I; demand(J, D) the hours D project J requires;
% cost(I, J, K) the cost K per hour of person I on project J; limit(I, J, L) the most hours L that person I
% can give project J (indices are 0-based, as in the data).

person(I) :- supply(I,_).
project(J) :- demand(J,_).

% bound(I,J,B): person I can work at most B hours on project J, which is the smaller of their supply and the limit
bound(I,J,B) :- person(I), project(J), supply(I,S), limit(I,J,L), B = #min { S ; L }.

% assign(I,J,H): person I works H hours on project J
1 { assign(I,J,H) : H = 0..B } 1 :- bound(I,J,B).

% the hours a person works on all projects equal their supply
:- supply(I,S), #sum { H,J : assign(I,J,H) } != S.

% the hours worked on a project by all people equal its demand
:- demand(J,D), #sum { H,I : assign(I,J,H) } != D.

% total_cost: the cost of all the hours worked
total_cost(C) :- C = #sum { H*K,I,J : assign(I,J,H), cost(I,J,K) }.

% the total cost is as small as possible
#minimize { H*K,I,J : assign(I,J,H), cost(I,J,K) }.

#show assign/3.
#show total_cost/1.
