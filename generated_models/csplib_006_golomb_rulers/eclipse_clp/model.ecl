% csplib_006_golomb_rulers: an ECLiPSe model from DCP Rosetta.
%
% Golomb ruler: a set of m integers 0 = a_1 < a_2 < ... < a_m such that the m(m-1)/2 differences
% a_j - a_i, for 1 <= i < j <= m, are all distinct. Such a ruler contains m marks and has length
% a_m. Find an optimal ruler, one of minimum length.
%
% Save this file as model.ecl. Download `csplib_006_golomb_rulers.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_006_golomb_rulers.json
%   eclipse -b model.ecl -e "run('csplib_006_golomb_rulers_1.dat'), halt"

% Field read from the data: size (the number of marks m of the ruler).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, ['length'-Length, 'marks'-Marks], min(Length)) :-
    memberchk(size-M, Instance),
    % the marks are positions in increasing order; M*M is an upper bound on the length of an optimal ruler with M marks (not given by the statement)
    length(Marks, M),
    Marks :: 0..M*M,
    nth1(1, Marks, First),
    First #= 0,
    Last is M - 1,
    ( for(I, 1, Last), param(Marks) do
        I1 is I + 1,
        nth1(I, Marks, Before),
        nth1(I1, Marks, After),
        Before #< After
    ),
    % the differences between every pair of marks are all distinct
    ( for(Left, 1, Last), foreach(DiffRow, DiffRows), param(Marks, M) do
        Start is Left + 1,
        ( for(Right, Start, M), foreach(Diff, DiffRow), param(Marks, Left) do
            nth1(Left, Marks, Ai),
            nth1(Right, Marks, Aj),
            Diff #= Aj - Ai
        )
    ),
    flatten(DiffRows, Diffs),
    alldifferent(Diffs),
    % the length of the ruler is the position of its last mark, to be minimized
    nth1(M, Marks, Length),
    Vars = Marks.

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
