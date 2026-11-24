% aircraft_landing: an ECLiPSe model from DCP Rosetta.
%
% Aircraft land on a single runway in a fixed sequence: the aircraft are numbered in the order they land. Each
% aircraft has an earliest and a latest possible landing time and a target landing time. Landing earlier than the
% target costs a penalty per unit of time, and so does landing later. Any two aircraft in the sequence must be
% separated by at least a minimum time, where the later one lands no sooner than the earlier one's landing time plus
% the separation time between them. Decide the exact landing time of each aircraft, within its window and the
% separations, so that the total penalty is as small as possible. Landing_times[I] is the landing time of aircraft I
% and total_penalty is the minimised total penalty.
%
% Save this file as model.ecl. Download `aircraft_landing.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py aircraft_landing.json
%   eclipse -b model.ecl -e "run('aircraft_landing_1.dat'), halt"

% Instance fields: earliest_landing and latest_landing (the time window of each aircraft), target_landing (the
% target time of each aircraft), penalty_before and penalty_after (the penalty per unit of time for landing before
% and after the target), separation_time (separation_time[I][J] is the minimum time between aircraft I and the later
% aircraft J, I before J in the sequence). All lists are indexed from 0 by aircraft.
:- lib(ic).
:- lib(listut).

model(Instance, Vars, [landing_times-Times, total_penalty-Penalty], min(Penalty)) :-
    memberchk(earliest_landing-Earliest, Instance),
    memberchk(latest_landing-Latest, Instance),
    memberchk(target_landing-Target, Instance),
    memberchk(penalty_before-PenaltyBefore, Instance),
    memberchk(penalty_after-PenaltyAfter, Instance),
    memberchk(separation_time-Separation, Instance),
    length(Earliest, N),
    length(Times, N),
    length(Earlies, N),                    % time units landed before the target
    length(Lates, N),                      % time units landed after the target
    % each aircraft lands within its time window
    % and the time it lands before or after its target is what the penalties are charged on
    ( foreach(T, Times), foreach(Ea, Earliest), foreach(Lt, Latest), foreach(Tg, Target),
      foreach(E, Earlies), foreach(La, Lates) do
        T :: Ea..Lt,
        EarlyMax is max(0, Tg - Ea),
        LateMax is max(0, Lt - Tg),
        E :: 0..EarlyMax,
        La :: 0..LateMax,
        E #>= Tg - T,
        La #>= T - Tg
    ),
    % the aircraft land in the given sequence, and each pair keeps its minimum separation
    ( for(I, 0, N-2), param(N, Times, Separation) do
        ( for(J, I+1, N-1), param(I, Times, Separation) do
            separated(I, J, Times, Separation)
        )
    ),
    % the total penalty of the landings before and after the targets, to be minimised
    Penalty #= PenaltyBefore * Earlies + PenaltyAfter * Lates,
    concat_list(Times, Tmp, Vars),
    concat_list(Earlies, Lates, Tmp).

% aircraft J lands at least the separation time of I and J after aircraft I lands
separated(I, J, Times, Separation) :-
    nth0(I, Times, TI),
    nth0(J, Times, TJ),
    nth0(I, Separation, SepRow),
    nth0(J, SepRow, Sep),
    TJ #>= TI + Sep.

concat_list([], Ys, Ys).
concat_list([X | Xs], Ys, [X | Zs]) :- concat_list(Xs, Ys, Zs).

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
