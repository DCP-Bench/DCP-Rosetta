% csplib_026_sports_tournament_scheduling: an ECLiPSe model from DCP Rosetta.
%
% Schedule a tournament of n teams over n-1 weeks, each week divided into n/2 periods, and each period divided into two
% slots. The first team in each slot plays at home, whilst the second plays the first team away. Every team plays once
% a week, every team plays at most twice in the same period over the tournament, and every team plays every other team.
%
% Save this file as model.ecl. Download `csplib_026_sports_tournament_scheduling.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_026_sports_tournament_scheduling.json
%   eclipse -b model.ecl -e "run('csplib_026_sports_tournament_scheduling_1.dat'), halt"
%
% The instance field: n_teams (the number of teams, n).

:- lib(ic).
:- lib(branch_and_bound).

% Outputs home and away: home[W][P] (away[W][P]) is the team playing at home (away) in week W, period P, counting from 1.
model(Instance, Vars, [home-Home, away-Away]) :-
    memberchk(n_teams-N, Instance),
    W is N - 1,                            % the number of weeks
    P is N // 2,                           % the number of periods in each week
    length(Home, W),
    ( foreach(Row, Home), param(P) do length(Row, P) ),
    length(Away, W),
    ( foreach(Row, Away), param(P) do length(Row, P) ),
    flatten(Home, HomeCells),
    flatten(Away, AwayCells),
    append(HomeCells, AwayCells, Vars),
    Vars :: 1..N,

    % the two teams of a slot are different, and the unordered pair of teams of each game gets a code
    ( foreach(H, HomeCells), foreach(A, AwayCells), foreach(Pid, Pids), param(N) do
        H #\= A,
        Lo #= min(H, A),
        Hi #= max(H, A),
        Pid #= (Lo - 1) * N + Hi
    ),

    % every team plays once a week: the 2P slots of each week hold each team exactly once
    ( foreach(HR, Home), foreach(AR, Away) do
        append(HR, AR, Week),
        alldifferent(Week)
    ),

    % every team plays every other team: each pair of teams occurs in exactly one game
    alldifferent(Pids),

    % every team plays at most twice in the same period over the tournament
    ( for(Period, 1, P), param(Home, Away, N) do
        ( foreach(HR, Home), foreach(X, HCol), param(Period) do element(Period, HR, X) ),
        ( foreach(AR, Away), foreach(Y, ACol), param(Period) do element(Period, AR, Y) ),
        append(HCol, ACol, Col),
        ( for(Team, 1, N), param(Col) do
            ( foreach(C, Col), foreach(B, Bs), param(Team) do B #= (C #= Team) ),
            sum(Bs) #=< 2
        )
    ).

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
