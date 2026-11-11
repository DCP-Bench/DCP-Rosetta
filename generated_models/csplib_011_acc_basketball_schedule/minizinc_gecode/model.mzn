% csplib_011_acc_basketball_schedule: a MiniZinc model from DCP Rosetta.
%
% Find a timetable for the 1997/98 Atlantic Coast Conference (ACC) in basketball. The 9 teams are
% Clemson (Clem), Duke (Duke), Florida State (FSU), Georgia Tech (GT), Maryland (UMD), North Carolina
% (UNC), North Carolina State (NCSt), Virginia (UVA) and Wake Forest (Wake). The problem is a double
% round-robin schedule for these 9 teams, in which each team plays each other once at home and once
% away, over 18 dates. The first and all subsequent odd dates are weekday fixtures, and the second and
% all subsequent even dates are weekend fixtures. The schedule must also satisfy the following.
%
% 1. Mirroring. The dates are grouped into pairs (r1, r2) such that each team plays the same team on
%    both dates, at home on one and away on the other. The scheme is (1,8), (2,9), (3,12), (4,13),
%    (5,14), (6,15), (7,16), (10,17), (11,18).
% 2. No two final aways. No team can play away on both last dates.
% 3. Home/away/bye pattern. No team may have more than two away matches in a row, nor more than two
%    home matches in a row. No team may have more than three away matches or byes in a row, nor more
%    than four home matches or byes in a row.
% 4. Weekend pattern. Over the weekends, each team plays four at home, four away and has one bye.
% 5. First weekends. Each team has home matches or byes on at least two of the first five weekends.
% 6. Rival matches. Every team except FSU has a traditional rival: Duke-UNC, Clem-GT, NCSt-Wake and
%    UMD-UVA. On the last date, every team except FSU plays its rival, unless it plays FSU or has a bye.
% 7. Constrained matches. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at least once on dates 11 to 18.
% 8. Opponent sequences. No team plays away against UNC and then Duke, or Duke and then UNC, on two
%    consecutive dates. No team plays UNC, Duke and Wake on three consecutive dates, in any order.
% 9. Other constraints. UNC plays Duke on the last date and on date 11, and plays Clem on date 2. Duke
%    has a bye on date 16. Wake does not play at home on date 17 and has a bye on date 1. Clem, Duke,
%    UMD and Wake do not play away on the last date. Clem, FSU, GT and Wake do not play away on date 1.
%    Neither FSU nor NCSt has a bye on the last date. UNC does not have a bye on date 1.
%
% Save this file as model.mzn. Download `csplib_011_acc_basketball_schedule.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_011_acc_basketball_schedule.json
%   minizinc model.mzn csplib_011_acc_basketball_schedule_1.json

include "globals.mzn";

int: n_teams;                                  % the number of teams
int: n_days;                                   % the number of dates

% the problem is the 9-team, 18-date ACC schedule below, with its fixed team numbers and rules
constraint assert(n_teams = 9 /\ n_days = 18, "the constraints are those of the 9-team, 18-date ACC problem");

set of int: Teams = 0..n_teams - 1;            % teams are numbered from 0
set of int: Days = 0..n_days - 1;              % dates are numbered from 0
int: n_byes = n_days - 2 * (n_teams - 1);      % byes per team: dates not spent meeting each other team twice

int: CLEM = 0;
int: DUKE = 1;
int: FSU = 2;
int: GT = 3;
int: UMD = 4;
int: UNC = 5;
int: NCSt = 6;
int: UVA = 7;
int: WAKE = 8;

int: HOME = 0;                                 % the team plays at home
int: BYE = 1;                                  % the team has a bye
int: AWAY = 2;                                 % the team plays away

% rival[t]: the traditional rival of team t (FSU has none, so it is its own)
array[Teams] of int: rival = array1d(Teams, [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]);

% config[d, t]: the opponent of team t on date d, or t itself for a bye
array[Days, Teams] of var Teams: config;
% venue[d, t]: whether team t is at home, away or has a bye on date d
array[Days, Teams] of var {HOME, BYE, AWAY}: venue;

% the opponents of the teams on each date are all different
constraint forall(d in Days)(all_different([config[d, t] | t in Teams]));

% if team t plays team j on a date, then team j plays team t
constraint forall(d in Days, t in Teams)(config[d, config[d, t]] = t);

% venues match the opponents: a match has one team at home and one away, and a bye is an opponent of itself
constraint forall(d in Days, t in Teams)(
    (venue[d, t] = HOME <-> (config[d, t] != t /\ venue[d, config[d, t]] = AWAY)) /\
    (venue[d, t] = AWAY <-> (config[d, t] != t /\ venue[d, config[d, t]] = HOME)) /\
    (venue[d, t] = BYE <-> config[d, t] = t));

% double round-robin: each team plays each other team exactly once at home
constraint forall(t in Teams, o in Teams where t != o)(
    sum(d in Days)(bool2int(config[d, t] = o /\ venue[d, t] = HOME)) = 1);

% redundant: each team meets every other team on exactly two dates, so it has n_days - 2 * (n_teams - 1) byes
constraint forall(t in Teams)(
    global_cardinality([config[d, t] | d in Days], [j | j in Teams],
                       [if j = t then n_byes else 2 endif | j in Teams]));

% redundant: each team plays n_teams - 1 matches at home and n_teams - 1 away
constraint forall(t in Teams)(sum(d in Days)(bool2int(venue[d, t] = HOME)) = n_teams - 1);
constraint forall(t in Teams)(sum(d in Days)(bool2int(venue[d, t] = AWAY)) = n_teams - 1);
constraint forall(t in Teams)(sum(d in Days)(bool2int(venue[d, t] = BYE)) = n_byes);

% redundant: on each date one team has a bye, and the other teams are split evenly between home and away
constraint forall(d in Days)(sum(t in Teams)(bool2int(venue[d, t] = BYE)) = 1);
constraint forall(d in Days)(sum(t in Teams)(bool2int(venue[d, t] = HOME)) = n_teams div 2);
constraint forall(d in Days)(sum(t in Teams)(bool2int(venue[d, t] = AWAY)) = n_teams div 2);

% 1. mirroring: a pair of mirrored dates repeats the same opponents, with the venues swapped
% (mirror[d] is the date paired with date d, counted from 0)
array[Days] of int: mirror = array1d(Days, [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]);
constraint forall(d in Days, t in Teams)(config[d, t] = config[mirror[d], t]);
constraint forall(d in Days, t in Teams)(venue[d, t] = 2 - venue[mirror[d], t]);

% 2. no two final aways: no team plays away on both last dates
constraint forall(t in Teams)(
    bool2int(venue[n_days - 2, t] = AWAY) + bool2int(venue[n_days - 1, t] = AWAY) <= 1);

% 3. home/away/bye pattern: limits on runs of away, home, away-or-bye and home-or-bye matches
constraint forall(t in Teams)(
    forall(d in 0..n_days - 3)(sum(k in 0..2)(bool2int(venue[d + k, t] = HOME)) <= 2) /\
    forall(d in 0..n_days - 3)(sum(k in 0..2)(bool2int(venue[d + k, t] = AWAY)) <= 2) /\
    forall(d in 0..n_days - 4)(sum(k in 0..3)(bool2int(venue[d + k, t] = AWAY \/ venue[d + k, t] = BYE)) <= 3) /\
    forall(d in 0..n_days - 5)(sum(k in 0..4)(bool2int(venue[d + k, t] = HOME \/ venue[d + k, t] = BYE)) <= 4));

% 4. weekend pattern: the weekends are the odd dates counted from 0, and over them each team
% plays four home matches, four away matches and has one bye
array[int] of int: weekends = [d | d in Days where d mod 2 = 1];
constraint forall(t in Teams)(
    sum(d in weekends)(bool2int(venue[d, t] = HOME)) = 4 /\
    sum(d in weekends)(bool2int(venue[d, t] = AWAY)) = 4 /\
    sum(d in weekends)(bool2int(venue[d, t] = BYE)) = 1);

% 5. first weekends: each team has a home match or a bye on at least two of the first five weekends
constraint forall(t in Teams)(
    sum(i in 1..5)(bool2int(venue[weekends[i], t] = HOME \/ venue[weekends[i], t] = BYE)) >= 2);

% 6. rival matches: on the last date, every team except FSU plays its rival, unless it plays FSU or has a bye
constraint forall(t in Teams where t != FSU)(
    config[n_days - 1, t] = rival[t] \/ config[n_days - 1, t] = FSU \/ venue[n_days - 1, t] = BYE);

% 7. constrained matches: these pairings occur at least once on dates 11 to 18 (counted from 0 as days 10 to 17)
constraint forall(p in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)])(
    sum(d in 10..n_days - 1)(bool2int(config[d, p.1] = p.2)) >= 1);

% 8. opponent sequences: no team (other than UNC and Duke) plays away against UNC and Duke on two
% consecutive dates, in either order
constraint forall(t in Teams where t != DUKE /\ t != UNC, d in 0..n_days - 2)(
    not (config[d, t] = UNC /\ venue[d, t] = AWAY /\ config[d + 1, t] = DUKE /\ venue[d + 1, t] = AWAY) /\
    not (config[d, t] = DUKE /\ venue[d, t] = AWAY /\ config[d + 1, t] = UNC /\ venue[d + 1, t] = AWAY));
% no team (other than UNC, Duke and Wake) plays UNC, Duke and Wake on three consecutive dates, home or away
constraint forall(t in Teams where t != UNC /\ t != DUKE /\ t != WAKE, d in 0..n_days - 3)(
    not forall(x in [UNC, DUKE, WAKE])(exists(k in 0..2)(config[d + k, t] = x)));

% 9. other constraints, with dates counted from 0
% UNC plays Duke on date 11 and on the last date
constraint config[10, UNC] = DUKE /\ config[n_days - 1, UNC] = DUKE;
% UNC plays Clem on date 2
constraint config[1, UNC] = CLEM;
% Duke has a bye on date 16
constraint venue[15, DUKE] = BYE;
% Wake does not play at home on date 17
constraint venue[16, WAKE] != HOME;
% Wake has a bye on date 1
constraint venue[0, WAKE] = BYE;
% Clem, Duke, UMD and Wake do not play away on the last date
constraint forall(t in [CLEM, DUKE, UMD, WAKE])(venue[n_days - 1, t] != AWAY);
% Clem, FSU, GT and Wake do not play away on date 1
constraint forall(t in [CLEM, FSU, GT, WAKE])(venue[0, t] != AWAY);
% neither FSU nor NCSt has a bye on the last date
constraint forall(t in [FSU, NCSt])(venue[n_days - 1, t] != BYE);
% UNC does not have a bye on date 1
constraint venue[0, UNC] != BYE;

solve satisfy;
output ["{\"config\": ", showJSON(config), ", \"where\": ", showJSON(venue), "}"];
