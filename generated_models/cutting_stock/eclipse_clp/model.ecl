% cutting_stock: an ECLiPSe model from DCP Rosetta.
%
% Cutting stock: raw rolls of a given width are cut with a set of cutting patterns. Each pattern, cut from one roll,
% yields a given number of pieces of each width, and for each width a number of pieces is ordered. Choose how many
% rolls to cut with each pattern so that at least the ordered number of pieces of each width is produced, minimising
% the total number of raw rolls cut.
%
% Save this file as model.ecl. Download `cutting_stock.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py cutting_stock.json
%   eclipse -b model.ecl -e "run('cutting_stock_1.dat'), halt"
%
% The data fields: num_patterns is the number of cutting patterns, num_rolls_width[I][J] the number of pieces of
% width J that pattern I yields from one roll, and orders[J] the number of pieces of width J ordered; lists are
% indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Used[I] is the number of rolls cut with pattern I.
model(Instance, Used, [patterns_used-Used, min_rolls_cut-Total], min(Total)) :-
    memberchk(num_patterns-P, Instance),
    memberchk(num_rolls_width-Pieces, Instance),
    memberchk(orders-Orders, Instance),
    length(Used, P),
    length(Orders, W),
    ( foreach(Order, Orders), fromto(0, S0, S1, Demand) do
        S1 is S0 + Order
    ),
    % no pattern is cut more often than the total number of pieces ordered, which keeps the search finite
    Used :: 0..Demand,

    % for each width, the pieces produced by all the rolls reach the ordered number of that width
    ( for(J, 1, W), param(Pieces, Orders, Used) do
        nth1(J, Orders, Order),
        width_pieces(Pieces, Used, J, Terms),
        sum(Terms) #>= Order
    ),

    % the total number of raw rolls cut
    Total #= sum(Used).

% Terms: for each pattern, the pieces of width J its rolls produce, times the number of rolls cut with it
width_pieces(Pieces, Used, J, Terms) :-
    ( foreach(Row, Pieces), foreach(U, Used), foreach(T, Terms), param(J) do
        nth1(J, Row, Piece),
        T #= Piece * U
    ).

search_goal(Used) :-
    search(Used, 0, first_fail, indomain_min, complete, []).
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
