% media_selection: a SWI-Prolog model from DCP Rosetta.
%
% The media selection problem is a problem of allocating advertising budgets between possible advertising outlets.
% Given a set of media options, determine which media should be selected so that all audiences are reached with
% minimum campaign cost. It does not matter if an audience is covered more than once, as long as it is covered at
% least once. The company does not wish to spend more money on the campaign than necessary.
%
% Save this file as model.pl. Download `media_selection.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('media_selection.json')" -t halt model.pl
%
% Data fields: target_audiences (the audiences to reach), advertising_media (the media options), incidence_matrix
% (incidence_matrix[A][M] is 1 when medium M reaches audience A, lists indexed from 0), media_costs (the cost of
% each medium, indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Selected-Cost, [is_selected-Selected, min_total_cost-Cost], min(Cost)) :-
    Audiences = Instance.target_audiences,
    Media = Instance.advertising_media,
    Reaches = Instance.incidence_matrix,
    Costs = Instance.media_costs,
    length(Audiences, NumAudiences),
    length(Media, NumMedia),
    length(Reaches, NumAudiences),
    % Selected[M] is 1 when medium M is bought, 0 otherwise
    length(Selected, NumMedia),
    Selected ins 0..1,
    % every audience is reached by at least one bought medium
    maplist({Selected}/[Row]>>scalar_product(Row, Selected, #>=, 1), Reaches),
    % the total cost of the media bought
    sum_list(Costs, CostTotal),
    Cost in 0..CostTotal,
    scalar_product(Costs, Selected, #=, Cost).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
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
