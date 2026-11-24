% csplib_002_template_design: an ECLiPSe model from DCP Rosetta.
%
% Template design: a colour printing firm makes sheets of board from a number of templates, each
% a thin aluminium sheet with a number of slots on which the designs of several variations of a
% product are etched. Decide, for a given number of templates with a given number of slots each,
% which variations and how many copies of each to place on each template, and how many sheets to
% produce from each template. Every slot of a template is filled, and each template produces
% between 1 sheet and as many sheets as the largest demand. The sheets produced must meet at
% least the demand of every variation, and the total number of sheets produced is to be minimized.
%
%
% Save this file as model.ecl. Download `csplib_002_template_design.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_002_template_design.json
%   eclipse -b model.ecl -e "run('csplib_002_template_design_1.dat'), halt"

% Fields read from the data: demand (the number of copies needed of each variation, indexed from
% 0; the number of variations is its length), n_slots (the number of slots on each template) and
% n_templates (the number of templates).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, ['layout'-Layout, 'production'-Production], min(Total)) :-
    memberchk(demand-Demand, Instance),
    memberchk(n_slots-Slots, Instance),
    memberchk(n_templates-NumTemplates, Instance),
    length(Demand, NumVar),
    ( foreach(D, Demand), fromto(0, In, Out, MaxDemand) do Out is max(In, D) ),
    % layout[T][V] is the number of copies of variation V on template T
    length(Layout, NumTemplates),
    ( foreach(RowT, Layout), param(NumVar, Slots) do
        length(RowT, NumVar),
        RowT :: 0..Slots,
        % every slot of the template is filled
        sum(RowT) #= Slots
    ),
    % each template produces between 1 sheet and as many sheets as the largest demand
    length(Production, NumTemplates),
    Production :: 1..MaxDemand,
    % the sheets produced from the templates meet the demand of every variation
    ( for(V, 1, NumVar), param(Layout, Production, Demand) do
        nth1(V, Demand, Need),
        ( foreach(Row, Layout), foreach(Pr, Production), foreach(Item, Items), param(V) do
            nth1(V, Row, Copies),
            Item #= Pr * Copies
        ),
        sum(Items) #>= Need
    ),
    % symmetry breaking (not in the statement): the templates are identical, so they are ordered by the number of
    % sheets they produce
    ( for(T, 1, NumTemplates - 1), param(Production) do
        nth1(T, Production, Before),
        T1 is T + 1,
        nth1(T1, Production, After),
        Before #>= After
    ),
    % the objective: the total number of sheets produced
    Total #= sum(Production),
    flatten(Layout, Flat),
    append(Production, Flat, Vars).

% label all the variables, the most constrained variable first and its smallest value first
search_goal(Vars) :- search(Vars, 0, first_fail, indomain_min, complete, []).

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
