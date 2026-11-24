% bus_scheduling: a clingo model from DCP Rosetta.
%
% Progress City is considering a mass-transit bus system to reduce in-city driving. The goal is to determine the minimum number of buses required to meet the transportation needs throughout the day. The demand for buses is approximated as constant over successive 4-hour intervals. Each bus can operate only 8 successive hours a day, so a bus that starts in one interval also works in the next one. The day is cyclic: the first interval follows the last.
%
% We need to ensure that the number of buses available in each 4-hour interval, those starting in it and those that started in the interval before, meets the demand for that interval.
%
% Save this file as model.lp. Download `bus_scheduling.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py bus_scheduling.json
%   python -m clingo model.lp bus_scheduling_1.lp

% Input: demands(I, D) holds the demand D for buses in the 4-hour interval I (indices are 0-based, in the order of the day).

slot(I) :- demands(I, _).
slots(N) :- N = #count { I : demands(I, _) }.

% a bus that starts in an interval is also available in the next one, and the day is cyclic
covers(I, I) :- slot(I).
covers(I, (I+1) \ N) :- slot(I), slots(N).

% the number of buses that start in each interval
% at most the total demand of buses ever needs to start in one interval, since starting each interval's
% demand in that interval already covers it; this only bounds the search
maxbuses(M) :- M = #sum { D, I : demands(I, D) }.
value(0..M) :- maxbuses(M).
1 { x(I, V) : value(V) } 1 :- slot(I).

% in each interval, the buses starting in it and in the interval before meet the demand
:- slot(J), demands(J, D), #sum { V, I : x(I, V), covers(I, J) } < D.

% the total number of buses is as small as possible
#minimize { V, I : x(I, V) }.

#show x/2.
