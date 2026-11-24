% csplib_026_sports_tournament_scheduling: a MiniZinc model from DCP Rosetta.
%
% The problem is to schedule a tournament of n teams over n-1 weeks, with each week divided into n/2 periods, and
% each period divided into two slots. The first team in each slot plays at home, whilst the second plays the first
% team away. A tournament must satisfy the following three constraints: every team plays once a week; every team
% plays at most twice in the same period over the tournament; every team plays every other team.
%
% Save this file as model.mzn. Download `csplib_026_sports_tournament_scheduling.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_026_sports_tournament_scheduling.json
%   minizinc model.mzn csplib_026_sports_tournament_scheduling_1.json

include "globals.mzn";

int: n_teams;                                     % the number of teams
set of int: Teams = 1..n_teams;                   % the teams are numbered from 1
set of int: Weeks = 1..n_teams - 1;               % the tournament lasts n - 1 weeks
set of int: Periods = 1..n_teams div 2;           % each week is divided into n / 2 periods

% home[w,p]: the team playing at home in week w and period p
array[Weeks, Periods] of var Teams: home;
% away[w,p]: the team playing away in week w and period p
array[Weeks, Periods] of var Teams: away;

% every team plays once a week
constraint forall(w in Weeks)(
    all_different([home[w, p] | p in Periods] ++ [away[w, p] | p in Periods]));

% every team plays at most twice in the same period over the tournament
constraint forall(p in Periods, t in Teams)(
    sum(w in Weeks)(bool2int(home[w, p] = t) + bool2int(away[w, p] = t)) <= 2);

% every team plays every other team once
constraint forall(s in Teams, t in Teams where s < t)(
    sum(w in Weeks, p in Periods)(
        bool2int((home[w, p] = s /\ away[w, p] = t) \/ (home[w, p] = t /\ away[w, p] = s))) = 1);

solve satisfy;

output ["{\"home\": ", showJSON(home), ", \"away\": ", showJSON(away), "}"];
