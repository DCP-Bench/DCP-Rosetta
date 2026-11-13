% session3_kidney_exchange: an ECLiPSe model from DCP Rosetta.
%
% At a hospital, n people are on a waiting list for a kidney transplant. Who can donate to whom is given as a
% directed graph: compatible[i] is the set of people to which person i can donate a kidney. People are numbered
% from 1. Choose the transplants that maximize the number of people who receive a new kidney, where anyone who
% gives a kidney must receive one and no person receives more than one kidney.
%
% Save this file as model.ecl. Download `session3_kidney_exchange.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session3_kidney_exchange.json
%   eclipse -b model.ecl -e "run('session3_kidney_exchange_1.dat'), halt"

% num_people: the number of people.
% compatible: for each person, indexed from 0 as in the JSON, the people (numbered from 1) that the person can donate to.

:- lib(ic).
:- lib(lists).
:- lib(listut).

% Gift: for each person (numbered from 1), the person they give a kidney to (a person gives at most one kidney),
% or the person themselves when they give none.
model(Instance, Gift, [transplants-Rows], max(sum(Gives))) :-
    memberchk(num_people-N, Instance),
    memberchk(compatible-Compatible, Instance),
    length(Gift, N),
    % a person gives to someone they are compatible with, or gives nothing (Gift[I] = I)
    ( for(I, 1, N), foreach(S, Gift), param(Compatible) do
        nth1(I, Compatible, Targets),
        S :: [I | Targets]
    ),
    % no person receives more than one kidney; the gifts then form a permutation, so every giver receives one
    alldifferent(Gift),
    % a person gives a kidney exactly when they do not give to themselves
    ( for(I, 1, N), foreach(S, Gift), foreach(G, Gives) do
        G #= (S #\= I)
    ),
    % transplants[i][j] is 1 when person i gives a kidney to person j
    ( for(I, 1, N), foreach(Row, Rows), param(Gift, N) do
        nth1(I, Gift, S),
        ( for(J, 1, N), foreach(T, Row), param(S, I) do
            ( J =:= I -> T = 0 ; T #= (S #= J) )
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
