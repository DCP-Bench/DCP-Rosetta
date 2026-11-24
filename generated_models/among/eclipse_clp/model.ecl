% among: an ECLiPSe model from DCP Rosetta.
%
% Find an array x of n integers between 0 and 7, inclusive, such that exactly m of them take one of the values in v.
% The other elements may take any other value in that range.
%
% Save this file as model.ecl. Download `among.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py among.json
%   eclipse -b model.ecl -e "run('among_1.dat'), halt"

% Instance fields: n (the length of the array x), m (how many of its elements take a value in v), v (the values,
% a list indexed from 0).
:- lib(ic).

model(Instance, Xs, [x-Xs]) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    memberchk(v-V, Instance),
    length(Xs, N),
    % each element of x is an integer between 0 and 7
    Xs :: 0..7,
    % each element is a hit when it takes one of the values in v: Hit is 1 for such an element, 0 otherwise
    ( foreach(X, Xs), foreach(Hit, Hits), param(V) do
        ( foreach(Vj, V), foreach(Eq, Eqs), param(X) do
            Eq #= (X #= Vj)
        ),
        Hit #= (sum(Eqs) #>= 1)
    ),
    % exactly m of the elements are hits
    sum(Hits) #= M.

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
