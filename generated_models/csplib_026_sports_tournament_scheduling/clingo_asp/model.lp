% csplib_026_sports_tournament_scheduling: a clingo model from DCP Rosetta.
%
% The problem is to schedule a tournament of n teams over n-1 weeks, with each week divided into n/2 periods, and each period divided into two slots. The first team in each slot plays at home, whilst the second plays the first team away. A tournament must satisfy the following three constraints: every team plays once a week; every team plays at most twice in the same period over the tournament; every team plays every other team.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
% Save this file as model.lp. Download `csplib_026_sports_tournament_scheduling.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_026_sports_tournament_scheduling.json
%   python -m clingo model.lp csplib_026_sports_tournament_scheduling_1.lp

% Input: n_teams(N): the number N of teams. The teams are numbered 1..N; the weeks are 0..N-2 and the
% periods are 0..N/2-1 (indices are 0-based, as in the output).

team(1..N) :- n_teams(N).
week(0..N-2) :- n_teams(N).
period(0..N/2-1) :- n_teams(N).

% home(W,P,T) and away(W,P,T): team T plays at home, or away, in period P of week W.
% Each slot of each period holds exactly one team.
1 { home(W,P,T) : team(T) } 1 :- week(W), period(P).
1 { away(W,P,T) : team(T) } 1 :- week(W), period(P).

% no team plays itself in the same period
:- home(W,P,T), away(W,P,T).

% every team plays once a week
:- week(W), team(T), #count { P,h : home(W,P,T) ; P,a : away(W,P,T) } != 1.

% every team plays at most twice in the same period over the tournament
:- period(P), team(T), #count { W,h : home(W,P,T) ; W,a : away(W,P,T) } > 2.

% every team plays every other team: the schedule has exactly n(n-1)/2 games, so each pair meets exactly once
:- team(T1), team(T2), T1 < T2,
   #count { W,P,1 : home(W,P,T1), away(W,P,T2) ; W,P,2 : home(W,P,T2), away(W,P,T1) } != 1.

#show home/3.
#show away/3.
