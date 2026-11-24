% session1_thick_as_thieves: an ECLiPSe model from DCP Rosetta.
%
% Following a robbery at Sparkles the Jeweller's, Inspector Korner of the Yard interviewed six of the usual suspects. He
% knew that the getaway car had been barely big enough to hold two, so he reckoned that at least four of them were
% innocent, but which ones? He also supposed that the innocent ones would tell the truth, while the guilty one or ones
% would lie. What they actually said was:
%   ARTIE: "It wasn't me."
%   BILL: "Crackitt was in it up to his neck."
%   CRACKITT: "No I wasn't."
%   DODGY: "If Crackitt did it, Bill did it with him."
%   EDGY: "Nobody did it alone."
%   FINGERS: "That's right: it was Artie and Dodgy together."
% If the good inspector's suppositions were correct, who is guilty?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% No data fields: the model reads no data, so the run block calls it with an empty list.
:- lib(ic).

% Outputs artie, bill, crackitt, dodgy, edgy, fingers: 1 when the suspect is guilty, 0 when innocent.
model(_Data, Vars, [artie-Artie, bill-Bill, crackitt-Crackitt, dodgy-Dodgy, edgy-Edgy, fingers-Fingers]) :-
    Vars = [Artie, Bill, Crackitt, Dodgy, Edgy, Fingers],
    Vars :: 0..1,

    % at least one of them is guilty
    sum(Vars) #>= 1,

    % at least four of them are innocent, so at most two are guilty
    sum(Vars) #=< 2,

    % each suspect tells the truth exactly when innocent, so each statement is true exactly when its speaker is innocent.
    % ARTIE: "It wasn't me." is true exactly when Artie is innocent, as it must be.
    % CRACKITT: "No I wasn't." is true exactly when Crackitt is innocent, as it must be.

    % BILL: "Crackitt was in it up to his neck." is true exactly when Crackitt is guilty, so Bill is guilty exactly
    % when Crackitt is innocent
    Crackitt #= 1 - Bill,

    % DODGY: "If Crackitt did it, Bill did it with him." is true unless Crackitt is guilty and Bill is not
    1 - Crackitt + Bill - (1 - Crackitt)*Bill #= 1 - Dodgy,

    % EDGY: "Nobody did it alone." is true when two of them did it (with at most two guilty and at least one, that is
    % when the count of guilty is 2)
    sum(Vars) - 1 #= 1 - Edgy,

    % FINGERS: "it was Artie and Dodgy together." is true when Artie and Dodgy are both guilty
    Artie*Dodgy #= 1 - Fingers.

:- lib(branch_and_bound).

% Solves the model and prints each output.
run :-
    solve_model([]).

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
