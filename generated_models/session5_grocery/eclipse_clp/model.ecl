% session5_grocery: an ECLiPSe model from DCP Rosetta.
%
% A kid buys some items in a grocery store, and the cashier charges a total price. The kid pays and is about to
% leave when the cashier calls the kid back: the cashier had multiplied the prices instead of adding them, and
% adding them still gives the same total price. Each price is a positive whole number of cents. Find the prices
% of the items, given that the sum and the product of the prices, in dollars, both equal the total price in
% dollars.
%
% Save this file as model.ecl. Download `session5_grocery.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py session5_grocery.json
%   eclipse -b model.ecl -e "run('session5_grocery_1.dat'), halt"

% num_items: the number of items.
% total_price: the total price in cents.

:- lib(ic).
:- lib(lists).

% Prices: the price of each item in cents, from the lowest to the highest.
model(Instance, Prices, [prices-Prices]) :-
    memberchk(num_items-N, Instance),
    memberchk(total_price-Total, Instance),
    length(Prices, N),
    Prices :: 1..Total,
    % symmetry break: the items are listed from the lowest price to the highest
    nondecreasing(Prices),
    % the prices in cents add up to the total price in cents
    sum(Prices) #= Total,
    % the product of the prices in dollars equals the total in dollars: the product of the prices
    % in cents is the total times 100 to the power N - 1
    Target is Total * 100^(N - 1),
    price_product(Prices, Target).

% P is the product of the numbers in Xs
price_product([X], X).
price_product([X | Xs], P) :-
    price_product(Xs, Q),
    P #= X * Q.

nondecreasing([]).
nondecreasing([_]).
nondecreasing([A, B | Rest]) :-
    A #=< B,
    nondecreasing([B | Rest]).

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
