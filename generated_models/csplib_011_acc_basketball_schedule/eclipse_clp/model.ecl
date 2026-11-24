% csplib_011_acc_basketball_schedule: an ECLiPSe model from DCP Rosetta.
%
% Find a double round-robin schedule for the 9 teams of the 1997/98 Atlantic Coast Conference basketball tournament
% (Clemson, Duke, Florida State, Georgia Tech, Maryland, North Carolina, North Carolina State, Virginia, Wake Forest),
% over 18 dates, each team playing each other once at home and once away. Odd dates are weekday fixtures, even dates
% weekend fixtures. The schedule must satisfy nine further sets of constraints, stated in the comments of the model:
% mirroring, final away matches, home/away/bye patterns, weekend patterns, first weekends, rival matches, constrained
% matches, opponent sequences and other fixed constraints.
%
% Save this file as model.ecl. Download `csplib_011_acc_basketball_schedule.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_011_acc_basketball_schedule.json
%   eclipse -b model.ecl -e "run('csplib_011_acc_basketball_schedule_1.dat'), halt"

% Instance fields: n_teams (the number of teams, 9) and n_days (the number of dates, 18). The schedule is the one of
% the 9 teams numbered 0 to 8 in the order Clemson, Duke, Florida State, Georgia Tech, Maryland, North Carolina,
% North Carolina State, Virginia, Wake Forest, over the 18 dates.
% Output config: config[D][I] is the opponent of team I on date D (I itself on a bye).
% Output where: where[D][I] is 0 when team I plays at home on date D, 2 when away, 1 when it has a bye.

:- lib(ic).
:- lib(ic_global).
:- lib(ic_mdd).
:- lib(listut).
:- import alldifferent/1 from ic_global.

model(Instance, Vars, Outputs) :-
    memberchk(n_teams-9, Instance),
    memberchk(n_days-18, Instance),
    % one row of opponents and one row of venues for each of the nine dates that carry free variables
    make_rows(9, Crs, Wrs),
    Crs = [R1,R2,R3,R4,R5,R6,R7,R8,R9],
    Wrs = [Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9],
    % the mirror dates take the venues of their partner, reversed
    mirror(Wrs, Vrs),
    Vrs = [P1,P2,P3,P4,P5,P6,P7,P8,P9],
    % the 18 dates in order: a mirroring pair (r1, r2) shares its opponents, so the date r2 repeats the row of r1
    % pairs (1,8) (2,9) (3,12) (4,13) (5,14) (6,15) (7,16) (10,17) (11,18)
    Cd = [R1,R2,R3,R4,R5,R6,R7,R1,R2,R8,R9,R3,R4,R5,R6,R7,R8,R9],
    Wd = [Q1,Q2,Q3,Q4,Q5,Q6,Q7,P1,P2,Q8,Q9,P3,P4,P5,P6,P7,P8,P9],
    venue_tuples(Tuples),
    % each date: the opponent and the venue of two teams agree, a bye is a team playing itself
    date_rules(Crs, Wrs),
    % each team meets each other team once over the nine first-of-pair dates, its bye is its own date
    % and its venue pattern over those dates is a legal one (rules 2 to 5, table below)
    team_rules(0, Crs, Wrs, Tuples),
    % rule 6: in the last date every team except FSU plays its rival, unless it plays FSU or has a bye
    rule6_last_date_rivals(Cd),
    % rule 7: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at least once in dates 11 to 18
    rule7_constrained_matches(Cd),
    % rule 8: opponent sequence constraints
    rule8_opponent_sequences(Cd, Wd),
    % rule 9: other constraints on fixed dates
    rule9_other_constraints(Cd, Wd),
    team_major(Wrs, WTeam),
    flatten(Crs, CRow),
    append(WTeam, CRow, Vars),
    Outputs = [config-Cd, where-Wd].

% the search labels the venues team by team, then the opponents, in input order, lowest value first
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).

% ---------------------------------------------------------------------------
% Structure: the nine first-of-pair dates carry the free variables, mirror dates copy them

make_rows(0, [], []) :- !.
make_rows(N, [C|Cs], [W|Ws]) :-
    N > 0,
    length(C, 9), C :: 0..8,            % the opponent of each team on this date
    length(W, 9), W :: 0..2,            % the venue of each team on this date: 0 home, 1 bye, 2 away
    N1 is N - 1,
    make_rows(N1, Cs, Ws).

% mirror rule (rule 1): a team plays at home on one date of a pair and away on the other, so the venue is reversed
mirror([], []).
mirror([W|Ws], [V|Vs]) :-
    length(V, 9), V :: 0..2,
    ( foreach(Wi, W), foreach(Vi, V) do Vi #= 2 - Wi ),
    mirror(Ws, Vs).

% the venues listed team by team (column I of the rows)
team_major(Rows, Flat) :- team_major(0, Rows, Flat).
team_major(9, _, []) :- !.
team_major(I, Rows, Flat) :-
    column(I, Rows, Col),
    I1 is I + 1,
    team_major(I1, Rows, Rest),
    append(Col, Rest, Flat).

column(_, [], []).
column(I, [R|Rs], [X|Xs]) :-
    nth0(I, R, X),
    column(I, Rs, Xs).

% ---------------------------------------------------------------------------
% Per-date structure: the opponents of a date form a matching, with byes as fixed points, and the venues agree with it

date_rules([], []).
date_rules([C|Cs], [W|Ws]) :-
    % each team meets one opponent or has a bye on this date
    alldifferent(C),
    date_cells(0, C, W),
    % redundant, implied by the double round robin (each team has two byes over the 18 dates and a date has at least
    % one): one bye, four home and four away matches among the eight teams that play
    occurrences(1, W, 1),
    occurrences(0, W, 4),
    occurrences(2, W, 4),
    date_rules(Cs, Ws).

date_cells(9, _, _) :- !.
date_cells(I, C, W) :-
    nth0(I, C, Ci),
    nth0(I, W, Wi),
    JP1 #= Ci + 1,
    % the opponent of my opponent is me
    element(JP1, C, IV), IV #= I,
    % the two teams of a match have opposite venues: one home, one away
    element(JP1, W, Wj),
    Wi + Wj #= 2,
    % a bye is exactly a team playing itself
    (Wi #= 1) <=> (Ci #= I),
    I1 is I + 1,
    date_cells(I1, C, W).

% each team meets each opponent once over the nine first-of-pair dates (a bye is the team itself), and its venue
% pattern over those dates is one of the legal patterns (rules 2 to 5)
team_rules(9, _, _, _) :- !.
team_rules(I, Crs, Wrs, Tuples) :-
    column(I, Crs, Col),
    alldifferent(Col),
    column(I, Wrs, WCol),
    table([WCol], Tuples),
    I1 is I + 1,
    team_rules(I1, Crs, Wrs, Tuples).

% ---------------------------------------------------------------------------
% Venue patterns (rules 2 to 5), enumerated over the nine first-of-pair dates. Venue values: 0 home, 1 bye, 2 away.

venue_tuples(Tuples) :-
    findall(S, (gen_seq(9, S), ok_pattern(S)), Tuples).

gen_seq(0, []) :- !.
gen_seq(N, [V|Vs]) :-
    N > 0,
    member(V, [0,1,2]),
    N1 is N - 1,
    gen_seq(N1, Vs).

% a team's venues over the 18 dates are S (dates 1 to 7 and 10 to 11) and their mirror (dates 8, 9, 12 to 18) in order
ok_pattern([S1,S2,S3,S4,S5,S6,S7,S8,S9]) :-
    M1 is 2 - S1, M2 is 2 - S2, M3 is 2 - S3, M4 is 2 - S4, M5 is 2 - S5,
    M6 is 2 - S6, M7 is 2 - S7, M8 is 2 - S8, M9 is 2 - S9,
    F = [S1,S2,S3,S4,S5,S6,S7,M1,M2,S8,S9,M3,M4,M5,M6,M7,M8,M9],
    % rule 2: no team plays away on both last dates (17 and 18)
    \+ (M8 =:= 2, M9 =:= 2),
    % rule 3: no more than two away matches in a row, no more than two home matches in a row, no more than three
    % away matches or byes in a row, no more than four home matches or byes in a row
    no_run(F, [2], 3),
    no_run(F, [0], 3),
    no_run(F, [1,2], 4),
    no_run(F, [0,1], 5),
    % rule 4: over the weekends (even dates) each team plays four at home, four away and has one bye
    E = [S2,S4,S6,M1,S8,M3,M5,M7,M9],
    cnt(0, E, 4),
    cnt(2, E, 4),
    cnt(1, E, 1),
    % rule 5: each team has home matches or byes on at least two of the first five weekends (dates 2, 4, 6, 8, 10)
    F5 = [S2,S4,S6,M1,S8],
    cnt(0, F5, H5),
    cnt(1, F5, B5),
    H5 + B5 >= 2.

% no run of K consecutive venues all in the set Set
no_run(L, Set, K) :-
    \+ ( append(_, T, L), append(P, _, T), length(P, K), all_in(P, Set) ).

all_in([], _).
all_in([X|Xs], Set) :-
    memberchk(X, Set),
    all_in(Xs, Set).

% the number of elements of the list equal to V
cnt(_, [], 0).
cnt(V, [X|Xs], N) :-
    (   X =:= V
    ->  cnt(V, Xs, N1), N is N1 + 1
    ;   cnt(V, Xs, N)
    ).

% ---------------------------------------------------------------------------
% Rule 6: rival matches. Teams: 0 Clemson, 1 Duke, 2 Florida State, 3 Georgia Tech, 4 Maryland, 5 North Carolina,
% 6 North Carolina State, 7 Virginia, 8 Wake Forest. Rivals: Duke-UNC, Clemson-GT, NCSt-Wake, UMD-UVA.

rival(0, 3).
rival(3, 0).
rival(1, 5).
rival(5, 1).
rival(6, 8).
rival(8, 6).
rival(4, 7).
rival(7, 4).

% in the last date, every team except FSU plays its rival, unless it plays FSU or has a bye
rule6_last_date_rivals(Cd) :-
    rule6_teams([0,1,3,4,5,6,7,8], Cd).

rule6_teams([], _).
rule6_teams([I|Is], Cd) :-
    rival(I, J),
    cell(18, I, Cd, X),
    ( X #= J ) or ( X #= 2 ) or ( X #= I ),
    rule6_teams(Is, Cd).

% ---------------------------------------------------------------------------
% Rule 7: constrained matches. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at least once in dates 11 to 18.

rule7_constrained_matches(Cd) :-
    constrained_pair(8, 5, Cd),
    constrained_pair(8, 1, Cd),
    constrained_pair(3, 5, Cd),
    constrained_pair(3, 1, Cd).

% team A plays team B on at least one date from 11 to 18
constrained_pair(A, B, Cd) :-
    ( for(D, 11, 18), foreach(Bool, Bools), param(A, B, Cd) do
        cell(D, A, Cd, X),
        Bool #= (X #= B)
    ),
    sum(Bools) #>= 1.

% ---------------------------------------------------------------------------
% Rule 8: opponent sequences. No team plays in two consecutive dates away against UNC and Duke, and no team plays in
% three consecutive dates against UNC, Duke and Wake (whatever the venues).

rule8_opponent_sequences(Cd, Wd) :-
    % two consecutive dates away against UNC (5) and Duke (1), in either order
    ( for(I, 0, 8), param(Cd, Wd) do
        ( for(D, 1, 17), param(I, Cd, Wd) do
            cell(D, I, Cd, C1), cell(D, I, Wd, W1),
            D1 is D + 1,
            cell(D1, I, Cd, C2), cell(D1, I, Wd, W2),
            ( C1 #\= 5 ) or ( W1 #\= 2 ) or ( C2 #\= 1 ) or ( W2 #\= 2 ),
            ( C1 #\= 1 ) or ( W1 #\= 2 ) or ( C2 #\= 5 ) or ( W2 #\= 2 )
        )
    ),
    % three consecutive dates against UNC (5), Duke (1) and Wake (8), in any order
    ( for(I, 0, 8), param(Cd) do
        ( for(D, 1, 16), param(I, Cd) do
            cell(D, I, Cd, A), D1 is D + 1, D2 is D + 2,
            cell(D1, I, Cd, B), cell(D2, I, Cd, C),
            ( A #\= 5 ) or ( B #\= 1 ) or ( C #\= 8 ),
            ( A #\= 5 ) or ( B #\= 8 ) or ( C #\= 1 ),
            ( A #\= 1 ) or ( B #\= 5 ) or ( C #\= 8 ),
            ( A #\= 1 ) or ( B #\= 8 ) or ( C #\= 5 ),
            ( A #\= 8 ) or ( B #\= 5 ) or ( C #\= 1 ),
            ( A #\= 8 ) or ( B #\= 1 ) or ( C #\= 5 )
        )
    ).

% ---------------------------------------------------------------------------
% Rule 9: other constraints on fixed dates

rule9_other_constraints(Cd, Wd) :-
    % UNC plays its rival Duke in the last date, and in date 11
    cell(18, 5, Cd, X18), X18 #= 1,
    cell(11, 5, Cd, X11), X11 #= 1,
    % UNC plays Clemson in the second date
    cell(2, 5, Cd, X2), X2 #= 0,
    % Duke has a bye in date 16
    cell(16, 1, Wd, V16), V16 #= 1,
    % Wake does not play at home in date 17
    cell(17, 8, Wd, V17), V17 #\= 0,
    % Wake has a bye in the first date
    cell(1, 8, Wd, V1w), V1w #= 1,
    % Clemson, Duke, Maryland and Wake do not play away in the last date
    forall_teams([0,1,4,8], 18, Wd, 2),
    % Clemson, FSU, GT and Wake do not play away in the first date
    forall_teams([0,2,3,8], 1, Wd, 2),
    % neither FSU nor NCSt has a bye in the last date
    forall_teams([2,6], 18, Wd, 1),
    % UNC does not have a bye in the first date
    cell(1, 5, Wd, V1u), V1u #\= 1.

% the teams of Is do not have venue V on date D
forall_teams([], _, _, _).
forall_teams([I|Is], D, Wd, V) :-
    cell(D, I, Wd, X),
    X #\= V,
    forall_teams(Is, D, Wd, V).

% ---------------------------------------------------------------------------
% Access to a date (1-based) and a team (0-based) in the 18-date list of rows

cell(D, I, Lst, X) :-
    nth1(D, Lst, Row),
    I1 is I + 1,
    nth1(I1, Row, X).

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).
