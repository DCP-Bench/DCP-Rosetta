% cabling: an ECLiPSe model from DCP Rosetta.
%
% Take a rack cabinet with a number of 1U devices, such as servers and routers. Some devices must be connected by cables,
% and some by several cables. Each device takes one position in the rack, and neighbouring positions are one unit apart.
% A cable between two devices is as long as the distance between their positions, so connecting them by k cables costs k
% times that distance. Place the devices in such an order that the sum of all cable lengths is as short as possible. Find
% the optimal sum of all cable lengths.
%
% Save this file as model.ecl. Download `cabling.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py cabling.json
%   eclipse -b model.ecl -e "run('cabling_1.dat'), halt"

% Fields read: n is the number of devices, devices is the list of their names, indexed from 0 as in the JSON, and
% cable_struct is the list of [device, device, number of cables] triples, each device given by its name.

:- lib(ic).
:- lib(listut).

% the position in the list of the device with the given name
device_index(Name, Devices, I) :- nth1(I, Devices, D), D == Name, !.

% Output final_sum: the total length of the cables, the value minimised.
model(Instance, Pos, [final_sum-Total], min(Total)) :-
    memberchk(n-N, Instance),
    memberchk(devices-Devices, Instance),
    memberchk(cable_struct-Cables, Instance),
    % each device takes one position in the rack, the positions are 1 to N, each used once
    length(Devices, N),
    length(Pos, N),
    Pos :: 1..N,
    alldifferent(Pos),
    % each cable of the connection between devices A and B adds the number of cables times the distance between their positions
    ( foreach([A, B, K], Cables), foreach(Length, Lengths), param(Devices, Pos) do
        device_index(A, Devices, I),
        device_index(B, Devices, J),
        nth1(I, Pos, PA),
        nth1(J, Pos, PB),
        Length #= K * abs(PA - PB)
    ),
    % the total length of all cables
    Total #= sum(Lengths).

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
