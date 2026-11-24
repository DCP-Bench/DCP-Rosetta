% csplib_011_acc_basketball_schedule: a clingo model from DCP Rosetta.
%
% Find a timetable for the 1997/98 Atlantic Coast Conference in basketball: a double round-robin schedule for the
% nine teams (Clemson, Duke, Florida State, Georgia Tech, Maryland, North Carolina, North Carolina State, Virginia
% and Wake Forest) over 18 dates, in which each team plays each other once at home and once away, subject to the
% constraints below. The first and all later odd dates are weekday fixtures, the second and all later even dates
% are weekend fixtures.
%
% Save this file as model.lp. Download `csplib_011_acc_basketball_schedule.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_011_acc_basketball_schedule.json
%   python -m clingo model.lp csplib_011_acc_basketball_schedule_1.lp
%
% Input: n_days(N): the number N of dates; n_teams(T): the number T of teams (indices are 0-based, as in the data).
% Teams are numbered from 0 in the order listed: 0 Clemson, 1 Duke, 2 Florida State, 3 Georgia Tech, 4 Maryland,
% 5 North Carolina, 6 North Carolina State, 7 Virginia, 8 Wake Forest. Dates are numbered from 0 (date 1 is 0).

day(0..N-1) :- n_days(N).
team(0..T-1) :- n_teams(T).

% the even-numbered dates of the problem (second, fourth, ...) are weekend fixtures, which are indices 1, 3, ...
weekend(D) :- day(D), D \ 2 == 1.

% on each date a team hosts one team, visits one team, or has a bye
1 { home(D,I,J) : team(J), J != I ; away(D,I,J) : team(J), J != I ; bye(D,I) } 1 :- day(D), team(I).

% a match is the same from both sides: if I hosts J then J visits I, and the other way round
:- home(D,I,J), not away(D,J,I).
:- away(D,I,J), not home(D,J,I).

% double round robin: each team hosts each other team exactly once
:- team(I), team(J), I != J, #count { D : home(D,I,J) } != 1.

hm(D,I) :- home(D,I,_).
aw(D,I) :- away(D,I,_).
game(D,I,J) :- home(D,I,J).
game(D,I,J) :- away(D,I,J).

% 1. mirroring: the dates of each pair (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16), (10,17), (11,18)
mirror(0,7). mirror(1,8). mirror(2,11). mirror(3,12). mirror(4,13). mirror(5,14). mirror(6,15). mirror(9,16). mirror(10,17).
% each team meets the same opponent on both dates of a pair, at home on one and away on the other, or has a bye on both
:- mirror(D1,D2), home(D1,I,J), not away(D2,I,J).
:- mirror(D1,D2), away(D1,I,J), not home(D2,I,J).
:- mirror(D1,D2), bye(D1,I), not bye(D2,I).
:- mirror(D1,D2), bye(D2,I), not bye(D1,I).

% 2. no two final aways: no team plays away on both of the last two dates
:- aw(16,I), aw(17,I).

% 3. no team has more than two away matches in a row, or more than two home matches in a row
:- aw(D,I), aw(D+1,I), aw(D+2,I).
:- hm(D,I), hm(D+1,I), hm(D+2,I).
% no team has more than three away matches or byes in a row, or more than four home matches or byes in a row
ab(D,I) :- aw(D,I).
ab(D,I) :- bye(D,I).
hb(D,I) :- hm(D,I).
hb(D,I) :- bye(D,I).
:- ab(D,I), ab(D+1,I), ab(D+2,I), ab(D+3,I).
:- hb(D,I), hb(D+1,I), hb(D+2,I), hb(D+3,I), hb(D+4,I).

% 4. weekend pattern: over the weekends each team plays four at home, four away and has one bye
:- team(I), #count { D : hm(D,I), weekend(D) } != 4.
:- team(I), #count { D : aw(D,I), weekend(D) } != 4.
:- team(I), #count { D : bye(D,I), weekend(D) } != 1.

% 5. first weekends: each team has home matches or byes on at least two of the first five weekends (dates 2 to 10)
:- team(I), #count { D : hb(D,I), weekend(D), D <= 9 } < 2.

% 6. rival matches: Duke-UNC, Clemson-Georgia Tech, NC State-Wake Forest, Maryland-Virginia
rival(1,5). rival(5,1). rival(0,3). rival(3,0). rival(6,8). rival(8,6). rival(4,7). rival(7,4).
% on the last date every team except FSU plays its rival, unless it plays FSU or has a bye
:- rival(I,R), not bye(17,I), not game(17,I,2), not game(17,I,R).

% 7. constrained matches: Wake Forest-UNC, Wake Forest-Duke, Georgia Tech-UNC and Georgia Tech-Duke occur on dates 11 to 18
:- #count { D : game(D,8,5), D >= 10 } = 0.
:- #count { D : game(D,8,1), D >= 10 } = 0.
:- #count { D : game(D,3,5), D >= 10 } = 0.
:- #count { D : game(D,3,1), D >= 10 } = 0.

% 8. opponent sequences: no team plays away against UNC and Duke on two consecutive dates
:- away(D,I,5), away(D+1,I,1).
:- away(D,I,1), away(D+1,I,5).
% no team plays against UNC, Duke and Wake Forest on three consecutive dates, home or away
sequence_opponent(1;5;8).
:- game(D,I,A), game(D+1,I,B), game(D+2,I,C), sequence_opponent(A), sequence_opponent(B), sequence_opponent(C), A != B, A != C, B != C.

% 9. other constraints
% UNC plays Duke on the last date and on date 11
:- not game(17,5,1).
:- not game(10,5,1).
% UNC plays Clemson on the second date
:- not game(1,5,0).
% Duke has a bye on date 16
:- not bye(15,1).
% Wake Forest does not play at home on date 17
:- hm(16,8).
% Wake Forest has a bye on the first date
:- not bye(0,8).
% Clemson, Duke, Maryland and Wake Forest do not play away on the last date
not_away_last(0;1;4;8).
:- not_away_last(I), away(17,I,_).
% Clemson, Florida State, Georgia Tech and Wake Forest do not play away on the first date
not_away_first(0;2;3;8).
:- not_away_first(I), away(0,I,_).
% neither Florida State nor NC State has a bye on the last date
:- bye(17,2).
:- bye(17,6).
% UNC does not have a bye on the first date
:- bye(0,5).

% config(D,I,J): team I plays team J on date D, or J is I for a bye; where(D,I,V): team I is at home (0),
% has a bye (1) or is away (2) on date D
config(D,I,J) :- game(D,I,J).
config(D,I,I) :- bye(D,I).
where(D,I,0) :- hm(D,I).
where(D,I,1) :- bye(D,I).
where(D,I,2) :- aw(D,I).

#show config/3.
#show where/3.
