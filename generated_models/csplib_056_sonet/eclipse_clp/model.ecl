% csplib_056_sonet: an ECLiPSe model from DCP Rosetta.
%
% SONET network design: the nodes are installed on rings through add-drop multiplexers (ADMs), one ADM for each node
% on each ring it is installed on. Two nodes with traffic demand between them must be on at least one common ring,
% and each ring has a capacity limiting the number of nodes it can host. Minimise the total number of ADMs used.
%
% Save this file as model.ecl. Download `csplib_056_sonet.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_056_sonet.json
%   eclipse -b model.ecl -e "run('csplib_056_sonet_1.dat'), halt"
%
% The data fields: n is the number of nodes, r the number of rings, capacity_nodes the number of nodes each ring can
% host (one per ring), demand the traffic demand between each pair of nodes; lists are indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Rows[K][I] is 1 when node I is installed on ring K, 0 otherwise.
model(Instance, Vars, [ring_config-Rows, total_adms-Total], min(Total)) :-
    memberchk(n-N, Instance),
    memberchk(r-R, Instance),
    memberchk(capacity_nodes-Capacities, Instance),
    memberchk(demand-Demand, Instance),
    length(Rows, R),
    ( foreach(Row, Rows), param(N) do
        length(Row, N),
        Row :: 0..1
    ),

    % each ring hosts no more nodes than its capacity
    ( foreach(Row, Rows), foreach(Cap, Capacities) do
        sum(Row) #=< Cap
    ),

    % two nodes with traffic demand between them must be on a common ring
    ( for(I, 0, N-2), param(Rows, Demand, N) do
        ( for(J, I+1, N-1), param(Rows, Demand, I) do
            ( traffic(Demand, I, J) -> share_ring(Rows, I, J) ; true )
        )
    ),

    % the total number of ADMs is the number of nodes installed on rings
    flatten(Rows, Vars),
    sum(Vars) #= Total.

% the demand between nodes I and J, in either direction, is positive
traffic(Demand, I, J) :-
    nth0(I, Demand, RowI), nth0(J, RowI, D1),
    nth0(J, Demand, RowJ), nth0(I, RowJ, D2),
    ( D1 > 0 ; D2 > 0 ).

% nodes I and J are both on some ring: the product of their flags is 1 on at least one ring
share_ring(Rows, I, J) :-
    ( foreach(Row, Rows), foreach(B, Both), param(I, J) do
        nth0(I, Row, XI), nth0(J, Row, XJ),
        B #= XI * XJ
    ),
    sum(Both) #>= 1.

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
