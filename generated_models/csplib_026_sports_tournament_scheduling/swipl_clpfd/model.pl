% csplib_026_sports_tournament_scheduling: a SWI-Prolog model from DCP Rosetta.
%
% Schedule a tournament of n teams over n-1 weeks. Each week is divided into n/2 periods, and each period has two
% slots: the first team in a slot plays at home and the second plays away. Every team plays once a week; every team
% plays at most twice in the same period over the tournament; and every team plays every other team.
% The teams are numbered from 1 to n.
%
% Save this file as model.pl. Download `csplib_026_sports_tournament_scheduling.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_026_sports_tournament_scheduling.json')" -t halt model.pl
%
% Data fields: n_teams (the number of teams n; n is even).
:- use_module(library(clpfd)).

model(Instance, Vars, [home-Home, away-Away]) :-
    N = Instance.n_teams,
    Weeks is N - 1,
    Periods is N // 2,
    NumPairs is N * (N - 1) // 2,
    % Games[W][P] is the number of the pair of teams that meet in week W, period P (pairs are numbered from 1)
    length(Games, Weeks),
    maplist(row_of_length(Periods), Games),
    append(Games, AllGames),
    AllGames ins 1..NumPairs,
    % Home[W][P] and Away[W][P] are the teams of that game, the first team in the slot plays at home
    length(Home, Weeks), maplist(row_of_length(Periods), Home),
    length(Away, Weeks), maplist(row_of_length(Periods), Away),
    append(Home, AllHome), append(Away, AllAway),
    AllHome ins 1..N, AllAway ins 1..N,
    pair_table(N, Table),
    maplist(game_teams(Table), AllGames, AllHome, AllAway),
    % every team plays every other team: the games are the NumPairs different pairs
    all_distinct(AllGames),
    % every team plays once a week: the slots of each week hold every team exactly once
    maplist(week_has_every_team, Home, Away),
    % every team plays at most twice in the same period over the tournament
    transpose(Home, HomeByPeriod),
    transpose(Away, AwayByPeriod),
    maplist(at_most_twice(N), HomeByPeriod, AwayByPeriod),
    % symmetry: the teams, the periods and the weeks can be renamed and reordered, and the two teams of a game swapped: the
    % first week has the games 1 v 2, 3 v 4, ..., the other weeks are listed by the pair of their first period,
    % and the team at home has the smaller number
    Games = [_|OtherGames],
    first_week(Home, Away),
    maplist(nth1(1), OtherGames, FirstGames),
    chain(FirstGames, #<),
    maplist(home_first, AllHome, AllAway),
    append([AllGames, AllHome, AllAway], Vars).

row_of_length(N, Row) :- length(Row, N).

first_week([HomeRow|_], [AwayRow|_]) :-
    length(HomeRow, Periods),
    numlist(1, Periods, Ps),
    maplist(first_game, Ps, HomeRow, AwayRow).

first_game(P, Home, Away) :- Home #= 2 * P - 1, Away #= 2 * P.

home_first(Home, Away) :- Home #< Away.

% the pairs I-J (I < J) of teams, as rows [Pair, Home, Away] in both orders
pair_table(N, Table) :-
    numlist(1, N, Teams),
    findall(I-J, ( member(I, Teams), member(J, Teams), I < J ), Pairs),
    pair_rows(Pairs, 1, Table).

pair_rows([], _, []).
pair_rows([I-J|Pairs], Id, [[Id, I, J], [Id, J, I]|Rows]) :-
    Id1 is Id + 1,
    pair_rows(Pairs, Id1, Rows).

game_teams(Table, Game, Home, Away) :-
    tuples_in([[Game, Home, Away]], Table).

week_has_every_team(HomeRow, AwayRow) :-
    append(HomeRow, AwayRow, Slots),
    all_distinct(Slots).

at_most_twice(N, HomeCol, AwayCol) :-
    append(HomeCol, AwayCol, Col),
    numlist(1, N, Teams),
    maplist(at_most_twice_pair, Teams, Pairs),
    global_cardinality(Col, Pairs).

at_most_twice_pair(Team, Team-Count) :- Count in 0..2.

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
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
