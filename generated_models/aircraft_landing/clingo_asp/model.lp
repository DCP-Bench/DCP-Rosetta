% aircraft_landing: a clingo model from DCP Rosetta.
%
% The Aircraft Landing Problem involves scheduling the landing of a set of aircraft on a single runway. Each aircraft has a specified time window (earliest and latest possible landing time) and a target landing time. Penalties are incurred for landing earlier or later than the target time. Additionally, a minimum separation time between the landings of any two aircraft must be respected. The landing sequence is fixed. The objective is to determine the exact landing time for each aircraft to minimize the total penalty, while respecting all time windows and separation constraints.
%
% Save this file as model.lp. Download `aircraft_landing.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py aircraft_landing.json
%   python -m clingo model.lp aircraft_landing_1.lp

% Input: earliest_landing(I, T) and latest_landing(I, T): the window of aircraft I; target_landing(I, T):
% its target time; penalty_before(I, P) and penalty_after(I, P): the penalty per unit of time it lands
% before or after its target; separation_time(I, J, S): the separation S between aircraft I and J
% (indices are 0-based, as in the data).

% Landing times are written as thresholds. ge(I, T) says aircraft I lands at time T or later, for
% each T after its earliest time and within its window. Thresholds of one aircraft are nested: if it
% lands at T or later, it lands at T - 1 or later too. This keeps the separation rule linear in the
% length of the windows, where naming every pair of landing times would grow with its square.
window(I, E+1..L) :- earliest_landing(I, E), latest_landing(I, L).
{ ge(I, T) } :- window(I, T).
:- ge(I, T+1), not ge(I, T), window(I, T).

% each aircraft lands at exactly one time: the last threshold it reaches (or its earliest time)
landing_times(I, E) :- earliest_landing(I, E), not ge(I, E+1).
landing_times(I, T) :- window(I, T), ge(I, T), not ge(I, T+1).

% the landing sequence is fixed: aircraft J lands after aircraft I whenever I < J. So if I lands at
% T or later, J lands at T + S or later, where S is the separation between them.
ge(J, T+S) :- ge(I, T), I < J, separation_time(I, J, S), window(J, T+S).
% the same holds from the earliest landing of I, and J must not be forced past its latest landing
ge(J, E+S) :- earliest_landing(I, E), I < J, separation_time(I, J, S), window(J, E+S).
:- ge(I, T), I < J, separation_time(I, J, S), latest_landing(J, L), T+S > L.
:- earliest_landing(I, E), I < J, separation_time(I, J, S), latest_landing(J, L), E+S > L.

% units of earliness: one for each time step T up to the target G at which aircraft I has not yet
% landed, so landing L before G costs G - L units
early_unit(I, T) :- window(I, T), target_landing(I, G), T <= G, not ge(I, T).
% a target after the latest landing: the aircraft is early for every step up to the target
early_unit(I, L+1..G) :- latest_landing(I, L), target_landing(I, G), G > L.

% units of lateness: one for each time step T after the target G at which aircraft I has landed,
% so landing L after G costs L - G units
late_unit(I, T) :- window(I, T), target_landing(I, G), T > G, ge(I, T).
% a target before the earliest landing: the aircraft is late for every step from the target up to its earliest time
late_unit(I, G+1..E) :- earliest_landing(I, E), target_landing(I, G), G < E.

% the total penalty is the sum of the penalties of all early and late units
total_penalty(P) :- P = #sum { PB, I, T, early : early_unit(I, T), penalty_before(I, PB) ;
                               PA, I, T, late : late_unit(I, T), penalty_after(I, PA) }.

% minimize the total penalty
#minimize { P : total_penalty(P) }.

#show landing_times/2.
#show total_penalty/1.
