% csplib_011_acc_basketball_schedule: a SWI-Prolog model from DCP Rosetta.
%
% Find a double round-robin timetable for 9 basketball teams (Clemson 0, Duke 1, Florida State 2, Georgia Tech 3,
% Maryland 4, North Carolina 5, North Carolina State 6, Virginia 7, Wake Forest 8) over 18 dates. Each team plays each
% other once at home and once away. Odd dates are weekdays, even dates weekends. The dates are paired by the mirroring
% scheme (1,8), (2,9), (3,12), (4,13), (5,14), (6,15), (7,16), (10,17), (11,18): a team meets the same opponent on both
% dates of a pair, at home on one and away on the other. The further rules are stated in the constraints below.
%
% Save this file as model.pl. Download `csplib_011_acc_basketball_schedule.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_011_acc_basketball_schedule.json')" -t halt model.pl
%
% Data fields: n_days (the number of dates), n_teams (the number of teams).
:- use_module(library(clpfd)).

% Opps[D][T] is the team that team T plays on date D (dates from 1, teams from 0), T itself for a bye.
% Wheres[D][T] is 0 for a home match, 2 for an away match and 1 for a bye.
model(Instance, Vars, Outputs) :-
    NDays = Instance.n_days,
    NTeams = Instance.n_teams,
    Last is NTeams - 1,
    % mirroring: the dates are grouped into pairs; the two dates of a pair have the same opponents
    Mirrors = [1-8, 2-9, 3-12, 4-13, 5-14, 6-15, 7-16, 10-17, 11-18],
    length(Mirrors, NPairs),
    length(PairOpps, NPairs),
    maplist(row_of_length(NTeams), PairOpps),
    length(FirstWheres, NPairs),
    maplist(row_of_length(NTeams), FirstWheres),
    append(PairOpps, OppVars),
    append(FirstWheres, WhereVars),
    append(WhereVars, OppVars, Vars),
    OppVars ins 0..Last,
    WhereVars ins 0..2,
    % a team has a bye exactly when it is its own opponent, and plays the team that plays it
    maplist(opponents_link(Last), PairOpps, FirstWheres),
    % each team plays each other team (once at home and once away: the two dates of a pair swap home and away),
    % so over the pairs of dates its opponents, itself for the bye, are all different
    transpose(PairOpps, OppsOfTeam),
    maplist(all_distinct, OppsOfTeam),
    % implied: on each date one team has a bye and the other teams play in pairs, half at home
    maplist(one_bye_rest_paired, FirstWheres),
    % the dates in order, from the pairs
    numlist(1, NDays, Dates),
    maplist(date_rows(Mirrors, PairOpps, FirstWheres), Dates, Opps, Wheres),
    numlist(0, Last, Teams),
    % no team plays away on both last dates (dates 17 and 18)
    no_double_away(Wheres, NDays),
    % home, away and bye runs: at most two away in a row, two home in a row, three away or byes, four home or byes
    maplist(runs_ok(Wheres), Teams),
    % each team has four home, four away and one bye on the weekends (even dates)
    findall(D, (between(1, NDays, D), D mod 2 =:= 0), Weekends),
    maplist(weekend_pattern(Wheres, Weekends), Teams),
    % each team has home matches or byes on at least two of the first five weekends
    maplist(early_weekends(Wheres), Teams),
    % rival matches on the last date (18): a team plays its rival, FSU or has a bye
    maplist(rival_last_date(Opps), [0-3, 1-5, 3-0, 4-7, 5-1, 6-8, 7-4, 8-6]),
    % Wake-UNC, Wake-Duke, GT-UNC and GT-Duke occur on dates 11 to 18
    numlist(11, 18, Late),
    maplist(meets_in(Opps, Late), [8-5, 8-1, 3-5, 3-1]),
    % no team plays away against UNC and Duke on two consecutive dates
    maplist(no_away_pair(Opps, Wheres, NDays), Teams),
    % no team plays UNC, Duke and Wake on three consecutive dates
    maplist(no_rival_triple(Opps, NDays), Teams),
    % the fixed matches and byes: UNC plays Duke on dates 18 and 11, UNC plays Clemson on date 2
    opp_var(Opps, 18, 5, Opp_18_5), Opp_18_5 #= 1,
    opp_var(Opps, 11, 5, Opp_11_5), Opp_11_5 #= 1,
    opp_var(Opps, 2, 5, Opp_2_5), Opp_2_5 #= 0,
    where_var(Wheres, 16, 1, Bye_16_1), Bye_16_1 #= 1,
    where_var(Wheres, 1, 8, Bye_1_8), Bye_1_8 #= 1,
    % UNC does not have a bye on the first date
    where_var(Wheres, 1, 5, Play_1_5), Play_1_5 #\= 1,
    % Wake does not play home on date 17
    where_var(Wheres, 17, 8, Home_17_8), Home_17_8 #\= 0,
    % Clemson, Duke, Maryland and Wake do not play away on the last date
    maplist(not_away_on(Wheres, 18), [0, 1, 4, 8]),
    % Clemson, FSU, GT and Wake do not play away on the first date
    maplist(not_away_on(Wheres, 1), [0, 2, 3, 8]),
    % neither FSU nor NC State have a bye on the last date
    maplist(not_bye_on(Wheres, 18), [2, 6]),
    Outputs = [config-Opps, where-Wheres].

row_of_length(N, Row) :- length(Row, N).

one_bye_rest_paired(Wheres) :-
    length(Wheres, NTeams),
    Games is (NTeams - 1) // 2,
    global_cardinality(Wheres, [1-1, 0-Games, 2-Games]).

% opponent of team T on date D, and where T plays on date D
opp_var(Opps, D, T, O) :- nth1(D, Opps, Row), nth0(T, Row, O).
where_var(Wheres, D, T, W) :- nth1(D, Wheres, Row), nth0(T, Row, W).

% team T has a bye (where 1) exactly when it is its own opponent; otherwise its opponent plays it, at home when it is away
opponents_link(Last, Opps, Wheres) :-
    numlist(0, Last, Teams),
    maplist(opponent_link(Opps, Wheres), Teams, Opps, Wheres).

opponent_link(Opps, Wheres, T, O, W) :-
    (O #= T) #<==> (W #= 1),
    O1 #= O + 1,
    element(O1, Opps, T),
    element(O1, Wheres, WO),
    W + WO #= 2.

% the rows of date D: its pair's opponents; the same wheres on the first date of the pair, swapped on the second
date_rows(Mirrors, PairOpps, FirstWheres, D, Opps, Wheres) :-
    nth1(K, Mirrors, First-Second),
    memberchk(D, [First, Second]),
    !,
    nth1(K, PairOpps, Opps),
    nth1(K, FirstWheres, FirstRow),
    (   D =:= First
    ->  Wheres = FirstRow
    ;   maplist(swap_where, FirstRow, Wheres)
    ).

% a home match on one date of a pair is an away match on the other, a bye (1) stays a bye
swap_where(W, S) :- S #= 2 - W.

% no team plays away on both of the last two dates (17 and 18)
no_double_away(Wheres, NDays) :-
    D17 is NDays - 1,
    nth1(D17, Wheres, W17),
    nth1(NDays, Wheres, W18),
    maplist(not_both_away, W17, W18).

not_both_away(A, B) :- (A #\= 2) #\/ (B #\= 2).

% no run of Len dates in which a team's where is in Values for more than Max of them
runs_ok(Wheres, Team) :-
    run_limit(Wheres, Team, [2], 3, 2),
    run_limit(Wheres, Team, [0], 3, 2),
    run_limit(Wheres, Team, [2, 1], 4, 3),
    run_limit(Wheres, Team, [0, 1], 5, 4).

run_limit(Wheres, Team, Values, Len, Max) :-
    length(Wheres, N),
    Last is N - Len + 1,
    numlist(1, Last, Starts),
    maplist(run_at(Wheres, Team, Values, Len, Max), Starts).

run_at(Wheres, Team, Values, Len, Max, Start) :-
    End is Start + Len - 1,
    numlist(Start, End, Days),
    maplist(where_in(Wheres, Team, Values), Days, Bs),
    sum(Bs, #=<, Max).

where_in(Wheres, Team, Values, Day, B) :-
    where_var(Wheres, Day, Team, W),
    values_flags(Values, W, Ps),
    sum(Ps, #=, B).

values_flags([], _, []).
values_flags([V|Vs], W, [P|Ps]) :-
    P #<==> (W #= V),
    values_flags(Vs, W, Ps).

% over the weekends each team has four home matches, four away matches and one bye
weekend_pattern(Wheres, Weekends, Team) :-
    maplist(where_var_of(Wheres, Team), Weekends, Ws),
    global_cardinality(Ws, [0-4, 2-4, 1-1]).

where_var_of(Wheres, Team, Day, W) :- where_var(Wheres, Day, Team, W).

count_days(Wheres, Days, Team, Values, K) :-
    maplist(where_in(Wheres, Team, Values), Days, Bs),
    sum(Bs, #=, K).

% over the first five weekends (dates 2, 4, 6, 8, 10) a team has a home match or a bye at least twice
early_weekends(Wheres, Team) :-
    count_days(Wheres, [2, 4, 6, 8, 10], Team, [0, 1], K),
    K #>= 2.

% on the last date (18) each team with a rival plays the rival, plays FSU, or has a bye
rival_last_date(Opps, Team-Rival) :-
    opp_var(Opps, 18, Team, O),
    O #= Rival #\/ O #= 2 #\/ O #= Team.

% the two teams meet on at least one of the given dates
meets_in(Opps, Dates, A-B) :-
    maplist(meets_on(Opps, A, B), Dates, Fs),
    sum(Fs, #>=, 1).

meets_on(Opps, A, B, D, F) :-
    opp_var(Opps, D, A, O),
    F #<==> (O #= B).

% team T does not play away against UNC (5) on date D and against Duke (1) on date D+1, nor the reverse
no_away_pair(Opps, Wheres, NDays, Team) :-
    Last is NDays - 1,
    numlist(1, Last, Ds),
    maplist(no_away_pair_at(Opps, Wheres, Team), Ds).

no_away_pair_at(Opps, Wheres, Team, D) :-
    D1 is D + 1,
    away_vs(Opps, Wheres, Team, D, 5, A),
    away_vs(Opps, Wheres, Team, D1, 1, B),
    A + B #=< 1,
    away_vs(Opps, Wheres, Team, D, 1, C),
    away_vs(Opps, Wheres, Team, D1, 5, E),
    C + E #=< 1.

away_vs(Opps, Wheres, Team, D, K, B) :-
    opp_var(Opps, D, Team, O),
    where_var(Wheres, D, Team, W),
    B #<==> (O #= K #/\ W #= 2).

% team T does not play UNC, Duke and Wake (against each of them, one each) on three consecutive dates
no_rival_triple(Opps, NDays, Team) :-
    Last is NDays - 2,
    numlist(1, Last, Ds),
    exclude(==(Team), [1, 5, 8], Rivals),
    maplist(no_triple_at(Opps, Rivals, Team), Ds).

no_triple_at(Opps, Rivals, Team, D) :-
    D1 is D + 1,
    D2 is D + 2,
    opp_var(Opps, D, Team, O1),
    opp_var(Opps, D1, Team, O2),
    opp_var(Opps, D2, Team, O3),
    values_flags(Rivals, O1, P1), sum(P1, #=, In1),
    values_flags(Rivals, O2, P2), sum(P2, #=, In2),
    values_flags(Rivals, O3, P3), sum(P3, #=, In3),
    B12 #<==> (O1 #\= O2),
    B13 #<==> (O1 #\= O3),
    B23 #<==> (O2 #\= O3),
    sum([In1, In2, In3, B12, B13, B23], #=<, 5).

% team T does not play away on date D (not_away_on), and does not have a bye on date D (not_bye_on)
not_away_on(Wheres, D, Team) :- where_var(Wheres, D, Team, W), W #\= 2.
not_bye_on(Wheres, D, Team) :- where_var(Wheres, D, Team, W), W #\= 1.

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
% the variable with the smallest domain first, ties broken by the most constraints on it
labeling_options([ffc]).

:- use_module(library(http/json)).
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
