% media_selection: an ECLiPSe model from DCP Rosetta.
%
% The main media selection problem is a problem of allocating advertising budgets between possible advertising outlets.
% Given a set of media options, it aims to determine which media should be selected so that all audiences are reached
% with minimum campaign cost. It does not matter if an audience is covered more than once, as long as it is covered at
% least once. Moreover, the company does not wish to spend more money on the campaign than necessary.
%
% Save this file as model.ecl. Download `media_selection.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py media_selection.json
%   eclipse -b model.ecl -e "run('media_selection_1.dat'), halt"
%
% The data fields: incidence_matrix[A][M] is 1 when media M reaches audience A, 0 otherwise (one row per audience,
% lists indexed from 0 as in the JSON); media_costs[M] is the cost of selecting media M. The number of media is the
% length of media_costs.

:- lib(ic).

% Outputs: is_selected[M] is 1 when media M is selected, 0 otherwise; min_total_cost is the total cost of the media
% selected.
model(Instance, Vars, [is_selected-Selected, min_total_cost-Total], min(Total)) :-
    memberchk(incidence_matrix-Incidence, Instance),
    memberchk(media_costs-MediaCosts, Instance),
    length(MediaCosts, NumMedia),
    length(Selected, NumMedia),

    % each media is either selected (1) or not (0)
    Selected :: 0..1,

    % every audience is reached by at least one of the selected media
    ( foreach(Reaching, Incidence), param(Selected) do
        Reaching * Selected #>= 1
    ),

    % the total cost of the selected media, which is to be as small as possible
    Total #= MediaCosts * Selected,

    Vars = Selected.

% the search picks the variable with the fewest candidate values first and tries the lowest value first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

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
