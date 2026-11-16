% session5_grocery: a SWI-Prolog model from DCP Rosetta.
%
% A kid goes into a grocery store and buys a number of items. The cashier charges a total price; the kid pays and is
% about to leave when the cashier calls the kid back and says that the cashier multiplied the items instead of adding
% them, and that with adding them the price still comes to the same total. What were the prices of the items? Each
% price is a positive whole number of cents, and the total price is given in cents. Both the sum and the product of
% the prices in dollars equal the total price in dollars.
%
% Save this file as model.pl. Download `session5_grocery.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session5_grocery.json')" -t halt model.pl
%
% Data fields: num_items (the number of items bought) and total_price (the total price, in cents).
:- use_module(library(clpfd)).

model(Instance, Prices, [prices-Prices]) :-
    Total = Instance.total_price,
    N = Instance.num_items,
    length(Prices, N),
    Prices ins 1..Total,                   % each price is a positive number of cents
    % the sum of the prices in cents is the total in cents, so the sums agree in dollars
    sum(Prices, #=, Total),
    % the product of the prices in dollars equals the total in dollars: the product in cents is
    % the total times 100^(N-1), since each of the N prices divides by 100 and the total by 100 once
    Target is Total * 100^(N - 1),
    foldl(times_into, Prices, 1, Product),
    Product #= Target.

times_into(Price, Acc0, Acc) :- Acc #= Acc0 * Price.

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
