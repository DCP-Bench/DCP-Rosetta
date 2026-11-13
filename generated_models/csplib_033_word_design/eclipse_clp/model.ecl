% csplib_033_word_design: an ECLiPSe model from DCP Rosetta.
%
% Find a set of num_words words of length n over the alphabet {A, C, G, T} such that each word has 4 symbols from {C, G},
% each pair of distinct words differ in at least 4 positions, and for each pair of words x and y in the set (where x and
% y may be identical) the reverse of x and the Watson-Crick complement of y differ in at least 4 positions. The
% complement replaces each A by a T and vice versa, and each C by a G and vice versa.
%
% Save this file as model.ecl. Download `csplib_033_word_design.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_033_word_design.json
%   eclipse -b model.ecl -e "run('csplib_033_word_design_1.dat'), halt"
%
% The instance fields: n (the length of each word), num_words (the number of words in the set).

:- lib(ic).
:- lib(branch_and_bound).
:- lib(listut).

% Output words: Words[W] is word W, its letters coded 1 for A, 2 for C, 3 for G and 4 for T.
model(Instance, Vars, [words-Words]) :-
    memberchk(n-N, Instance),
    memberchk(num_words-W, Instance),
    length(Words, W),
    ( foreach(Row, Words), param(N) do length(Row, N) ),
    flatten(Words, Vars),
    Vars :: 1..4,

    % each word has 4 symbols from {C, G}: the letters 2 and 3 are counted per word
    ( foreach(Row, Words) do
        ( foreach(X, Row), foreach(B, Bs) do element(X, [0, 1, 1, 0], B) ),
        sum(Bs) #= 4
    ),

    % each pair of distinct words differ in at least 4 positions
    ( for(A, 1, W), param(Words, N, W) do
        ( for(B, 1, W), param(Words, A, N) do
            (   B > A
            ->  nth1(A, Words, RowA),
                nth1(B, Words, RowB),
                ( foreach(X, RowA), foreach(Y, RowB), foreach(E, Es) do E #= (X #= Y) ),
                sum(Es) #=< N - 4
            ;   true
            )
        )
    ),

    % the reverse of x and the complement of y differ in at least 4 positions, for every pair x, y (x = y allowed)
    % the complement of a letter L is 5 - L: A (1) and T (4), C (2) and G (3)
    ( for(A, 1, W), param(Words, N, W) do
        reverse_of(Words, A, RevA),
        ( for(B, 1, W), param(Words, RevA, N) do
            nth1(B, Words, RowB),
            ( foreach(X, RevA), foreach(Y, RowB), foreach(E, Es) do E #= (X + Y #= 5) ),
            sum(Es) #=< N - 4
        )
    ).

% the reverse of word A of the set
reverse_of(Words, A, RevA) :-
    nth1(A, Words, RowA),
    reverse(RowA, RevA).

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
