% mario: an ECLiPSe model from DCP Rosetta.
%
% Mario needs to collect as much gold as possible by visiting houses. He starts at Mario's house and ends at Luigi's
% house, and the route returns from Luigi's house to Mario's house. Each house has a certain amount of gold, and the
% travel from one house to the next consumes fuel. Mario has a limited amount of fuel, and he must plan his route to
% maximize the gold collected without exceeding the fuel limit. Houses that are not on the route are left out.
%
% Save this file as model.ecl. Download `mario.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py mario.json
%   eclipse -b model.ecl -e "run('mario_1.dat'), halt"
%
% The data fields: nHouses is the number of houses N, numbered from 0; marioHouse and luigiHouse are the houses of
% Mario and of Luigi; fuelLimit is the fuel Mario has; arc_fuel[I][J] is the fuel used to travel from house I to
% house J; goldInHouse[I] is the gold in house I. All lists are indexed from 0 as in the JSON.

:- lib(ic).

% Output s: s[I] is the house that follows house I on the route, and s[I] = I when house I is not on the route.
model(Instance, Vars, [s-S], max(Gold)) :-
    memberchk(nHouses-N, Instance),
    memberchk(marioHouse-M, Instance),
    memberchk(luigiHouse-L, Instance),
    memberchk(fuelLimit-FuelLimit, Instance),
    memberchk(arc_fuel-ArcFuel, Instance),
    memberchk(goldInHouse-GoldInHouse, Instance),
    numbers_from(0, N, Houses),

    % s[I] is a house, and the successors of the houses are all different
    length(S, N),
    S :: 0..N-1,
    alldifferent(S),

    % Pos[I] is the place of house I on the route, counting from 0 at Mario's house
    length(Pos, N),
    Pos :: 0..N-1,
    MarioIdx is M + 1,
    element(MarioIdx, Pos, 0),

    % Mario's house is on the route: he leaves it for another house
    element(MarioIdx, S, MarioNext),
    MarioNext #\= M,

    % Luigi's house is followed by Mario's house
    LuigiIdx is L + 1,
    element(LuigiIdx, S, M),

    % Vis[I] is 1 when house I is on the route, 0 when it is left out
    length(Vis, N),
    Vis :: 0..1,

    ( foreach(Si, S), foreach(I, Houses), foreach(Vi, Vis), param(N) do
        Vi #= (Si #\= I)
    ),

    % the route goes on from each house on it: the successor of house I is the house with the next place on the
    % route, unless it is Mario's house (the end of the route, at Luigi's house)
    ( foreach(Si, S), foreach(I, Houses), foreach(Pi, Pos), foreach(Vi, Vis), param(M, N, Pos) do
        ( for(J, 0, N-1), param(Si, Pi, Vi, M, Pos) do
            (   J =:= M
            ->  true
            ;   J1 is J + 1,
                nth_item(J1, Pos, PJ),
                ((Vi #= 1) and (Si #= J)) => (PJ #= Pi + 1)
            )
        )
    ),

    % the fuel used on each arc of the route, and no fuel on the houses left out
    ( foreach(Si, S), foreach(I, Houses), foreach(Vi, Vis), foreach(Fi, Fuels), foreach(ArcRow, ArcFuel), param(N) do
        ( for(J, 0, N-1), param(Si, Vi, Fi, ArcRow) do
            J1 is J + 1,
            nth_item(J1, ArcRow, AJ),
            ((Vi #= 1) and (Si #= J)) => (Fi #= AJ)
        ),
        (Vi #= 0) => (Fi #= 0)
    ),

    % the fuel used on the route is at most the fuel limit of Mario
    sum(Fuels) #=< FuelLimit,

    % the gold collected is the gold of the houses on the route
    Gold #= GoldInHouse * Vis,

    app(S, Pos, T1),
    app(T1, Vis, T2),
    app(T2, Fuels, Vars).

% the I-th item of a list, counting from 1
nth_item(1, [X | _], X) :- !.
nth_item(I, [_ | Xs], X) :-
    I > 1,
    I1 is I - 1,
    nth_item(I1, Xs, X).

% the list of integers from From up to, not including, To
numbers_from(From, To, [From | Rest]) :-
    From < To,
    !,
    Next is From + 1,
    numbers_from(Next, To, Rest).
numbers_from(_, _, []).

app([], Ys, Ys).
app([X | Xs], Ys, [X | Zs]) :-
    app(Xs, Ys, Zs).

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
