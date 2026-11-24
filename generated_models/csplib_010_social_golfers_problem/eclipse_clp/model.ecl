% csplib_010_social_golfers_problem: an ECLiPSe model from DCP Rosetta.
%
% A golf club has n_groups * group_size golfers, each of whom plays golf once a week, always in n_groups groups of
% group_size golfers. Schedule the play of these golfers over n_weeks weeks, such that no golfer plays in the same
% group as any other golfer on more than one occasion.
%
% Save this file as model.ecl. Download `csplib_010_social_golfers_problem.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_010_social_golfers_problem.json
%   eclipse -b model.ecl -e "run('csplib_010_social_golfers_problem_1.dat'), halt"

% Instance fields: n_groups (the number of groups in each week), group_size (the number of golfers in each group),
% n_weeks (the number of weeks). Output assign: assign[I][J] is the 0-based group of golfer I in week J.

:- lib(ic).
:- lib(ic_global).
:- lib(listut).

model(Instance, Vars, [assign-Rows]) :-
    memberchk(n_groups-Groups, Instance),
    memberchk(group_size-GroupSize, Instance),
    memberchk(n_weeks-Weeks, Instance),
    Golfers is Groups * GroupSize,         % the number of golfers
    MaxGroup is Groups - 1,                % groups are numbered from 0
    length(Rows, Golfers),                 % one row per golfer
    ( foreach(Row, Rows), param(Weeks, MaxGroup) do
        length(Row, Weeks),                % one column per week
        Row :: 0..MaxGroup                 % the group of this golfer in each week
    ),
    flatten(Rows, Vars),
    % every week, each group holds exactly group_size golfers
    ( for(Week, 1, Weeks), param(Rows, Groups, GroupSize) do
        column(Rows, Week, Col),
        ( for(G, 0, Groups - 1), param(Col, GroupSize) do
            occurrences(G, Col, GroupSize)
        )
    ),
    % no golfer plays in the same group as another golfer on more than one occasion
    pair_limits(Rows).

% the search picks the golfers' assignments with the fewest candidate groups first, lowest group first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% the groups of all golfers in week Week (1-based)
column(Rows, Week, Col) :-
    ( foreach(R, Rows), foreach(X, Col), param(Week) do
        nth1(Week, R, X)
    ).

% every pair of golfers shares at most one week in the same group
pair_limits([]).
pair_limits([R|Rs]) :-
    ( foreach(R2, Rs), param(R) do
        same_group_at_most_once(R, R2)
    ),
    pair_limits(Rs).

% two golfers, given their rows, are in the same group in at most one week
same_group_at_most_once(R1, R2) :-
    ( foreach(X, R1), foreach(Y, R2), foreach(B, Bs) do
        B #= (X #= Y)                      % 1 when the two golfers share a group in that week
    ),
    Bs :: 0..1,
    sum(Bs) #=< 1.

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
