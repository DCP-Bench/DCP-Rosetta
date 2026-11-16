% capital_budget: a SWI-Prolog model from DCP Rosetta.
%
% A company is considering a number of investments. Each investment yields a net present value (NPV) and requires a
% certain cash outflow at the present time. The total budget available for investment is limited. Choose the
% investments so that the total cash outflow fits the budget and the total NPV obtained is as large as possible.
%
% Save this file as model.pl. Download `capital_budget.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('capital_budget.json')" -t halt model.pl
%
% Data fields: budget (the total budget available), cash_flow (the cash outflow of each investment), npv (the net
% present value of each investment), lists indexed from 0.
:- use_module(library(clpfd)).

model(Instance, Vars, [x-Xs, z-Total], max(Total)) :-
    Budget = Instance.budget,
    CashFlow = Instance.cash_flow,
    Npv = Instance.npv,
    length(Npv, N),                        % the number of investments
    length(Xs, N),
    Xs ins 0..1,                           % Xs[I] = 1 when investment I is chosen
    % the cash outflows of the chosen investments do not exceed the budget
    scalar_product(CashFlow, Xs, #=<, Budget),
    % the total NPV of the chosen investments, to be maximised
    scalar_product(Npv, Xs, #=, Total),
    Vars = [Total|Xs].

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
