% session1_guards_and_apples: an ECLiPSe model from DCP Rosetta.
%
% A boy wants to give an apple to a girl. To get to her, he has to pass through a number of gates, each with a guard.
% He bribes each guard with half of his apples, plus one. The boy does not have a knife, therefore he gives the guard an
% integer number of apples. After he has given the apple to the girl, he has no apples left, so he has exactly one apple
% after the last gate.
%
% Save this file as model.ecl. Download `session1_guards_and_apples.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session1_guards_and_apples.json
%   eclipse -b model.ecl -e "run('session1_guards_and_apples_1.dat'), halt"
%
% The data field: num_gates is the number of gates, each with a guard.

:- lib(ic).

% Output apples: the number of apples before each gate, then after the last gate (num_gates + 1 numbers).
model(Instance, Vars, [apples-Apples]) :-
    memberchk(num_gates-NumGates, Instance),
    NumPoints is NumGates + 1,
    length(Apples, NumPoints),
    length(Halves, NumGates),
    append(Apples, Halves, Vars),
    % no count exceeds the apples before the first gate, which is below 2^(num_gates+2)
    Max is 2 ^ (NumGates + 2),
    Vars :: 0..Max,

    % he passes the gates one after another, starting with the apples he has before the first gate
    passes(Apples, Halves).

% passes(Apples, Halves): Apples holds the apples before each gate, then the apples after the last gate; Halves holds
% half of the apples he has before each gate.
passes([Last], []) :-
    % after the last gate he has exactly one apple, for the girl
    Last #= 1.
passes([Before, After | Rest], [Half | Halves]) :-
    % half of the apples he has before a gate is a whole number of apples
    2*Half #= Before,
    % the guard is paid half of the apples plus one
    Bribe #= Half + 1,
    % the apples left after the gate are the apples before it less the bribe
    After #= Before - Bribe,
    passes([After | Rest], Halves).

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
