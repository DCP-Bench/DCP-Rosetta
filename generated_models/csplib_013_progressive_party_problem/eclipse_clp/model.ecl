% csplib_013_progressive_party_problem: an ECLiPSe model from DCP Rosetta.
%
% Timetable a party at a yacht club. Certain boats are designated hosts, and the crews of the remaining boats in turn
% visit the host boats for several successive half-hour periods. The crew of a host boat remains on board to act as
% hosts, while the crew of a guest boat together visits several hosts. Every boat can hold a limited number of people
% (its capacity), and the total number of people aboard a boat, including the host crew and the guest crews, must not
% exceed that capacity. A guest boat cannot revisit a host, and guest crews cannot meet more than once. Minimise the
% number of host boats.
%
% Save this file as model.ecl. Download `csplib_013_progressive_party_problem.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_013_progressive_party_problem.json
%   eclipse -b model.ecl -e "run('csplib_013_progressive_party_problem_1.dat'), halt"

% Instance fields: n_boats (the number of boats), n_periods (the number of half-hour periods), capacity (the capacity
% of each boat, a list indexed from 0) and crew_size (the number of people in the crew of each boat, a list indexed
% from 0). Outputs: is_host[B] is 1 when boat B is a host; visits[P][B] is the boat that boat B visits in period P
% (a host visits itself, so visits[P][H] = H). Boats are numbered from 0.

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Vars, Outputs, min(sum(IsHost))) :-
    memberchk(n_boats-N, Instance),
    memberchk(n_periods-P, Instance),
    memberchk(capacity-Cap, Instance),
    memberchk(crew_size-Crew, Instance),
    Nm1 is N - 1,
    Nm2 is N - 2,
    % IsHost[B] = 1 when boat B is a host
    length(IsHost, N),
    IsHost :: 0..1,
    % Visits[P][B] = the boat that boat B visits in period P
    length(Visits, P),
    ( foreach(Row, Visits), param(N, Nm1) do
        length(Row, N),
        Row :: 0..Nm1
    ),

    % a host boat stays where it is, so it visits itself in every period, and every guest visits a host
    ( foreach(Row, Visits), param(IsHost, Nm1) do
        ( for(B, 0, Nm1), param(IsHost, Row, Nm1) do
            nth0(B, IsHost, H),
            nth0(B, Row, V),
            (H #= 1) => (V #= B),
            I #= V + 1,
            element(I, IsHost, 1)
        )
    ),

    % Bs[P][G][H] = 1 when guest G is at host H in period P
    ( foreach(Row, Visits), foreach(Bp, Bs), param(N) do
        visit_flags(Row, N, Bp)
    ),

    % the total number of people aboard a host, including its own crew when it is a host and the crews of the
    % guest boats visiting it, does not exceed its capacity
    ( foreach(Bp, Bs), param(IsHost, Cap, Crew, N) do
        capacity_period(Bp, IsHost, Cap, Crew, N)
    ),

    % a guest boat cannot revisit a host: each guest visits each other boat at most once
    % (host boats visit themselves every period, so their own pairs are skipped)
    ( for(G, 0, Nm1), param(Bs, Nm1) do
        ( for(H, 0, Nm1), param(Bs, G, Nm1) do
            ( G =:= H ->
                true
            ;   flag_list(Bs, G, H, Xs),
                sum(Xs) #=< 1
            )
        )
    ),

    % guest crews cannot meet more than once: two boats share a host in at most one period. The constraint is
    % posted for all pairs; pairs involving a host are implied by the revisit rule above, and two hosts never share
    % a place.
    ( for(G1, 0, Nm2), param(Visits, Nm1, Nm2) do
        G1p is G1 + 1,
        ( for(G2, G1p, Nm1), param(Visits, G1, Nm1) do
            ( foreach(Row, Visits), foreach(M, Ms), param(G1, G2) do
                nth0(G1, Row, V1),
                nth0(G2, Row, V2),
                M :: 0..1,
                M #= (V1 #= V2)
            ),
            sum(Ms) #=< 1
        )
    ),

    flatten(Visits, FlatVisits),
    append(IsHost, FlatVisits, Vars),
    Outputs = [is_host-IsHost, visits-Visits].

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% the visit flags of one period: Bp[G][H] = 1 when boat G visits host H
visit_flags(Row, N, Bp) :-
    Nm1 is N - 1,
    ( for(G, 0, Nm1), foreach(BG, Bp), param(Row, Nm1) do
        ( for(H, 0, Nm1), foreach(X, BG), param(Row, G, Nm1) do
            nth0(G, Row, V),
            X :: 0..1,
            X #= (V #= H)
        )
    ).

% the load of each boat in one period: the host crew (when the boat is a host) plus the crews of the guest boats
% visiting it must not exceed its capacity
capacity_period(Bp, IsHost, Cap, Crew, N) :-
    Nm1 is N - 1,
    sum(Crew, Tot),
    ( for(H, 0, Nm1), param(Bp, IsHost, Cap, Crew, Nm1, Tot) do
        nth0(H, IsHost, IH),
        nth0(H, Cap, CH),
        nth0(H, Crew, CrH),
        S0 #= CrH * IH,
        ( for(G, 0, Nm1), fromto(S0, In, Out, Load), param(Bp, H, Crew, Nm1, Tot) do
            Out :: 0..Tot,
            ( G =:= H ->
                Out #= In
            ;   nth0(G, Bp, BG),
                nth0(H, BG, X),
                nth0(G, Crew, CG),
                Out #= In + CG * X
            )
        ),
        Load #=< CH
    ).

% the flags of guest G against host H, one per period
flag_list(Bs, G, H, Xs) :-
    ( foreach(Bp, Bs), foreach(X, Xs), param(G, H) do
        nth0(G, Bp, BG),
        nth0(H, BG, X)
    ).

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
