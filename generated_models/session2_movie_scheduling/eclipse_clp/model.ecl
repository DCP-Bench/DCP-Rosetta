% session2_movie_scheduling: an ECLiPSe model from DCP Rosetta.
%
% Consider the following scheduling problem. Imagine you are a highly-in-demand actor, who has been presented with offers
% to star in n different movie projects under development. Each offer comes specified with the first and last day of
% filming. To take the job, you must commit to being available throughout this entire period. Thus, you cannot
% simultaneously accept two jobs whose intervals overlap. For an artist such as yourself, the criteria for job
% acceptance is clear: you want to make as much money as possible. Because each of these films pays the same fee per
% film, this implies you seek the largest possible set of jobs (intervals) such that no two of them conflict with each
% other.
%
% Save this file as model.ecl. Download `session2_movie_scheduling.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_movie_scheduling.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session2_movie_scheduling.json
%   eclipse -b model.ecl -e "run('session2_movie_scheduling_1.dat'), halt"
%
% The data field: movies lists the offers in order, each as [title, first day, last day] (the first and last day of
% filming, both included).

:- lib(ic).
:- lib(listut).

% Output selected_movies: 1 when the movie is accepted, 0 otherwise, in the order of the movies.
model(Instance, Xs, [selected_movies-Xs], max(sum(Xs))) :-
    memberchk(movies-Movies, Instance),
    ( foreach([_Title, First, Last], Movies), foreach(First, Starts), foreach(Last, Ends) do
        true
    ),
    length(Movies, NMovies),
    length(Xs, NMovies),
    Xs :: 0..1,

    % two movies whose filming days share a day cannot both be accepted
    ( for(I, 1, NMovies), param(NMovies, Starts, Ends, Xs) do
        nth1(I, Starts, SI), nth1(I, Ends, EI),
        NextI is I + 1,
        ( for(J, NextI, NMovies), param(I, Starts, Ends, Xs, SI, EI) do
            nth1(J, Starts, SJ), nth1(J, Ends, EJ),
            ( SI =< EJ, SJ =< EI ->
                nth1(I, Xs, XI), nth1(J, Xs, XJ), XI + XJ #=< 1
            ;   true
            )
        )
    ).

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
