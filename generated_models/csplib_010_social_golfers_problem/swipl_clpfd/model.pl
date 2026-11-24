% csplib_010_social_golfers_problem: a SWI-Prolog model from DCP Rosetta.
%
% The coordinator of a local golf club has n_groups * group_size golfers, each of whom plays golf once a week, always
% in n_groups groups of group_size golfers. Find a schedule of play over n_weeks weeks such that no golfer plays in
% the same group as any other golfer on more than one occasion.
%
% Save this file as model.pl. Download `csplib_010_social_golfers_problem.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_010_social_golfers_problem.json')" -t halt model.pl
%
% Data fields: group_size (the number of golfers in each group), n_groups (the number of groups each week), n_weeks
% (the number of weeks).
:- use_module(library(clpfd)).

model(Instance, Vars, [assign-Rows]) :-
    GroupSize = Instance.group_size,
    NumGroups = Instance.n_groups,
    NumWeeks = Instance.n_weeks,
    NumGolfers is NumGroups * GroupSize,   % the golfers, n_groups groups of group_size each
    MaxGroup is NumGroups - 1,
    % Rows[G][W] is the group of golfer G in week W
    length(Rows, NumGolfers),
    maplist(row_of_length(NumWeeks), Rows),
    append(Rows, GroupVars),
    GroupVars ins 0..MaxGroup,
    % in each week every group has exactly group_size golfers
    transpose(Rows, Weeks),
    findall(G-GroupSize, between(0, MaxGroup, G), Counts),
    maplist(week_groups(Counts), Weeks),
    % Same[P][W] is 1 when the two golfers of pair P are in the same group in week W
    Last is NumGolfers - 1,
    findall(I-J, (between(0, Last, I), I1 is I + 1, between(I1, Last, J)), Pairs),
    maplist(pair_flags(Rows), Pairs, Items),
    % no two golfers are in the same group in more than one week
    maplist(meets_at_most_once, Items),
    % each golfer has group_size - 1 groupmates in every week (implied, helps the search)
    numlist(0, Last, Golfers),
    maplist(groupmates(GroupSize, Items), Golfers),
    % the flags are the search variables, then the group numbers
    maplist(item_flags, Items, FlagLists),
    append(FlagLists, FlagVars),
    append(FlagVars, GroupVars, Vars).

row_of_length(N, Row) :- length(Row, N).

% every group has the given counts of golfers in the week
week_groups(Counts, Week) :- global_cardinality(Week, Counts).

% the flags of the golfers I and J, one per week: 1 when they share a group that week
pair_flags(Rows, I-J, I-J-Fs) :-
    nth0(I, Rows, RI),
    nth0(J, Rows, RJ),
    maplist(same_group, RI, RJ, Fs).

same_group(A, B, S) :- S #<==> (A #= B).

% the two golfers share a group in at most one week
meets_at_most_once(_-_-Fs) :- sum(Fs, #=<, 1).

item_flags(_-_-Fs, Fs).

% the pairs that contain golfer G
pair_with(G, I-J-_) :- ( I =:= G ; J =:= G ).

% golfer G has group_size - 1 groupmates in each week
groupmates(GroupSize, Items, G) :-
    include(pair_with(G), Items, Sel),
    maplist(item_flags, Sel, Gs),
    transpose(Gs, WeekFlags),
    Need is GroupSize - 1,
    maplist(sum_is(Need), WeekFlags).

sum_is(Need, Fs) :- sum(Fs, #=, Need).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
