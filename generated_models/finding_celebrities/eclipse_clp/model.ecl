% finding_celebrities: an ECLiPSe model from DCP Rosetta.
%
% Given a list of people at a party and for each person the list of people they know at the party, find the
% celebrities. A celebrity is a person that everybody at the party knows but that only knows other celebrities.
% At least one celebrity is present at the party. Find whether each person is a celebrity.
%
% Save this file as model.ecl. Download `finding_celebrities.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py finding_celebrities.json
%   eclipse -b model.ecl -e "run('finding_celebrities_1.dat'), halt"

% Data fields: graph (the matrix of acquaintance, a list of rows indexed from 0: graph[I][J] is 1 when person I
% knows person J). The diagonal of the matrix is not used: nobody is judged by whether they know themselves.

:- lib(ic).
:- lib(listut).

model(Instance, Cs, [celebrities-Cs]) :-
    memberchk(graph-Graph, Instance),
    length(Graph, N),
    length(Cs, N),
    % each person is a celebrity (1) or not (0)
    Cs :: 0..1,
    % at least one celebrity is present at the party
    sum(Cs) #>= 1,
    (   for(I, 1, N), param(Graph, Cs, N) do
        nth1(I, Cs, CI),
        nth1(I, Graph, RowI),
        % over the other people J: whether J knows I, and whether I knows J while J is not a celebrity
        (   for(J, 1, N), param(Graph, Cs, I, RowI),
            fromto(1, In, Out, EveryoneKnows),
            fromto(Unmet, UIn, UOut, []) do
            (   J =:= I
            ->  Out = In, UOut = UIn
            ;   nth1(J, Graph, RowJ), nth1(I, RowJ, JKnowsI),
                nth1(J, RowI, IKnowsJ),
                nth1(J, Cs, CJ),
                Out is In * JKnowsI,
                UIn = [IKnowsJ * (1 - CJ) | UOut]
            )
        ),
        % person I is a celebrity if and only if everybody else knows them and everyone they know is a celebrity
        (CI #= 1) <=> ((EveryoneKnows #= 1) and (sum(Unmet) #= 0))
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
