% three_sum: an ECLiPSe model from DCP Rosetta.
%
% Given a collection of integers, find exactly m elements that sum to zero.
%
% Save this file as model.ecl. Download `three_sum.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py three_sum.json
%   eclipse -b model.ecl -e "run('three_sum_1.dat'), halt"

% Data fields: m (the number of elements to select), nums (the integers, a list indexed from 0).
% Output indices: indices[I] is 1 when element I is selected, 0 otherwise.
:- lib(ic).

model(Instance, Selected, [indices-Selected]) :-
    memberchk(m-M, Instance),
    memberchk(nums-Nums, Instance),
    length(Nums, N),                       % the number of integers
    length(Selected, N),
    Selected :: 0..1,                      % each element is either selected or not
    % exactly m elements are selected
    sum(Selected) #= M,
    % the selected elements sum to zero
    Total #= Nums * Selected,
    Total #= 0.

search_goal(Selected) :-
    search(Selected, 0, first_fail, indomain_min, complete, []).

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
