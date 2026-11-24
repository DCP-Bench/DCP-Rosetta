% csplib_013_progressive_party_problem: a clingo model from DCP Rosetta.
%
% A yacht club rally timetables a party at which certain boats are designated hosts, and the crews of the remaining
% boats in turn visit the host boats for several successive half-hour periods. The crew of a host boat remains on
% board to act as hosts, while the crew of a guest boat visits several hosts. Every boat can hold only a limited number
% of people at a time (its capacity), and the total number of people aboard a boat, including the host crew and the
% guest crews, must not exceed it. A guest boat cannot revisit a host, and guest crews cannot meet more than once.
% Minimize the number of host boats.
%
% Save this file as model.lp. Download `csplib_013_progressive_party_problem.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_013_progressive_party_problem.json
%   python -m clingo model.lp csplib_013_progressive_party_problem_1.lp
%
% Input: n_boats(N), n_periods(P): the number of boats N and of periods P; capacity(B,C) and crew_size(B,S): the capacity C
% and the crew size S of boat B (indices are 0-based, as in the data).

boat(0..N-1) :- n_boats(N).
period(0..P-1) :- n_periods(P).

% host(B): boat B is designated a host
{ host(B) : boat(B) }.

% visits(P,B,V): in period P boat B is at boat V; a host stays where it is, and a guest visits exactly one host
visits(P,B,B) :- period(P), host(B).
1 { visits(P,B,V) : host(V) } 1 :- period(P), boat(B), not host(B).

% the people aboard a host, its own crew and the guest crews that visit it, do not exceed its capacity
:- host(V), period(P), capacity(V,C), #sum { S,B : visits(P,B,V), crew_size(B,S) } > C.

% a guest boat visits each host at most once
:- boat(B), host(V), B != V, #count { P : visits(P,B,V) } > 1.

% together(P,B1,B2): the guest crews B1 and B2 meet in period P, at the same host
together(P,B1,B2) :- visits(P,B1,V), visits(P,B2,V), B1 < B2, not host(B1), not host(B2).

% guest crews do not meet more than once
:- boat(B1), boat(B2), B1 < B2, #count { P : together(P,B1,B2) } > 1.

% the number of host boats is as small as possible
#minimize { 1,B : host(B) }.

% is_host(B,V): boat B is (true) or is not (false) a host
is_host(B,true) :- host(B).
is_host(B,false) :- boat(B), not host(B).

#show visits/3.
#show is_host/2.
