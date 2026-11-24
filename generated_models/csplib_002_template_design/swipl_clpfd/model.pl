% csplib_002_template_design: a SWI-Prolog model from DCP Rosetta.
%
% A colour printing firm makes several design variations of a product from templates: thin aluminium sheets on
% which the designs for several variations are etched, one design per slot. Each printed sheet is made from a
% template. Choose, for a given number of templates with a given number of slots each, which variations and how
% many copies of each go on each template, and how many sheets are printed from each template. Every slot of a
% template is filled, and each template is printed between 1 sheet and as many sheets as the largest demand. The
% sheets printed must meet at least the demand of every variation, and the total number of printed sheets is to be
% minimized.
%
% Save this file as model.pl. Download `csplib_002_template_design.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_002_template_design.json')" -t halt model.pl
%
% Data fields: n_templates (the number of templates), n_slots (the number of slots on each template), n_var (the
% number of variations), demand (the number of copies needed of each variation, lists indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [production-Production, layout-Layout], min(Total)) :-
    NTemplates = Instance.n_templates,
    NSlots = Instance.n_slots,
    NVar = Instance.n_var,
    Demand = Instance.demand,
    max_list(Demand, MaxDemand),
    % Production[T] is the number of sheets printed from template T
    length(Production, NTemplates),
    Production ins 1..MaxDemand,
    % Layout[T][V] is the number of slots of template T that carry variation V
    length(Layout, NTemplates),
    maplist(template_row(NVar, NSlots), Layout),
    % the copies printed of each variation meet its demand
    transpose(Layout, ByVariation),
    maplist(meets_demand(Production), ByVariation, Demand),
    % the total number of sheets printed
    sum(Production, #=, Total),
    Vars = [Layout, Production, Total].

% a template has NVar variations, each with a count of slots, and every slot is filled
template_row(NVar, NSlots, Row) :-
    length(Row, NVar),
    Row ins 0..NSlots,
    sum(Row, #=, NSlots).

% sheets printed from each template, times the slots holding the variation, add up to at least the demand
meets_demand(Production, Slots, Need) :-
    maplist(printed_copies, Production, Slots, Copies),
    sum(Copies, #>=, Need).

printed_copies(Sheets, Slots, Copies) :-
    Copies #= Sheets * Slots.

:- use_module(library(http/json)).

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
