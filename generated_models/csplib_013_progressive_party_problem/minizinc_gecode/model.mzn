% csplib_013_progressive_party_problem: a MiniZinc model from DCP Rosetta.
%
% A party is timetabled at a yacht club. Certain boats are designated hosts, and the crews of the
% remaining boats in turn visit the host boats for several successive half-hour periods. The crew
% of a host boat remains on board to act as host, while the crew of a guest boat together visits
% several hosts. Every boat can only hold a limited number of people at a time (its capacity), and
% crew sizes differ. The total number of people aboard a boat, including the host crew and the guest
% crews, must not exceed its capacity. A guest boat cannot revisit a host, and guest crews cannot
% meet more than once. Minimise the number of host boats.
%
% Save this file as model.mzn. Download `csplib_013_progressive_party_problem.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_013_progressive_party_problem.json
%   minizinc model.mzn csplib_013_progressive_party_problem_1.json

include "globals.mzn";

int: n_boats;                               % the number of boats
int: n_periods;                             % the number of visiting periods
array[int] of int: capacity;                % capacity[b]: most people boat b can hold at once
array[int] of int: crew_size;               % crew_size[b]: number of people in the crew of boat b

set of int: Boats = 1..n_boats;             % one index per boat
set of int: Periods = 1..n_periods;         % one index per period

% is_host[b]: boat b is a host boat
array[Boats] of var bool: is_host;
% visits[p, b]: the boat whose crew boat b's crew is on during period p (numbered from 1 here,
% printed from 0)
array[Periods, Boats] of var Boats: visits;

% a host crew stays on its own boat in every period
constraint forall(b in Boats)(is_host[b] -> forall(p in Periods)(visits[p, b] = b));

% only host boats are visited
constraint forall(p in Periods, b in Boats)(is_host[visits[p, b]]);

% in each period, the people aboard a boat (its host crew and the guest crews visiting it) do not
% exceed its capacity
constraint forall(p in Periods, b in Boats)(
    sum(c in Boats)(bool2int(visits[p, c] = b) * crew_size[c]) <= capacity[b]);

% a guest boat does not revisit a host: it visits each host in at most one period
constraint forall(b in Boats where not is_host[b])(all_different([visits[p, b] | p in Periods]));

% two crews meet, that is are on the same boat in the same period, at most once
constraint forall(c1, c2 in Boats where c1 < c2)(
    sum(p in Periods)(bool2int(visits[p, c1] = visits[p, c2])) <= 1);

% minimise the number of host boats
var int: objective = sum(b in Boats)(bool2int(is_host[b]));
solve minimize objective;

output ["{\"visits\": ",
        showJSON(array2d(Periods, Boats, [fix(visits[p, b]) - 1 | p in Periods, b in Boats])),
        ", \"is_host\": ", showJSON(is_host), "}"];
