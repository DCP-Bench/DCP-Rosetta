% broken_weights: an ECLiPSe model from DCP Rosetta.
%
% A merchant had a measuring weight that broke into a number of pieces as the result of a fall. Each piece weighs a whole
% number of pounds, the pieces together weigh the total weight of the broken measure, and the pieces can be used on a
% balance scale, placed on either side of it, to weigh every integral weight from 1 to the total weight. Find the weights
% of the pieces.
%
% Save this file as model.ecl. Download `broken_weights.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py broken_weights.json
%   eclipse -b model.ecl -e "run('broken_weights_1.dat'), halt"

% Fields read: m is the total weight in pounds, n is the number of pieces.

:- lib(ic).
:- lib(listut).
:- lib(lists).

% Output weights: the weight of each piece.
model(Instance, Vars, [weights-Weights]) :-
    memberchk(m-M, Instance),
    memberchk(n-N, Instance),
    length(Weights, N),
    % each piece weighs a positive whole number of pounds, and the pieces weigh the total weight together
    Weights :: 1..M,
    sum(Weights) #= M,
    % every whole weight T from 1 to M is weighed: some pieces go on the same side of the scale as the object (-1), some on the other
    % side (1), the rest are not used (0), and the pieces so chosen balance the weight T
    ( for(T, 1, M), fromto([], In, Out, Choices), param(N, Weights) do
        length(Choice, N),
        Choice :: -1..1,
        Weights * Choice #= T,
        Out = [Choice | In]
    ),
    flatten([Weights, Choices], Vars).

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
