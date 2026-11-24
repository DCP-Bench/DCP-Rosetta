% crew: an ECLiPSe model from DCP Rosetta.
%
% Assign flight attendants (cabin crew) to flights. Each flight needs a certain number of
% cabin crew, and they have to speak certain languages. Each person has a role (steward or
% hostess) and speaks some languages (French, Spanish, German); one person can count towards
% several of the requirements of a flight. Every cabin crew member has at least two flights
% off after an attended flight, so nobody attends more than one of any three consecutive flights.
%
% Save this file as model.ecl. Download `crew.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py crew.json
%   eclipse -b model.ecl -e "run('crew_1.dat'), halt"

% Fields read from the data: attributes (for each person, indexed from 0, five 0/1 values:
% steward, hostess, speaks French, speaks Spanish, speaks German) and required_crew (for each
% flight, indexed from 0, six numbers: the number of cabin crew, then the numbers of stewards,
% hostesses, French, Spanish and German speakers needed).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [crew-Crew]) :-
    memberchk(attributes-Attributes, Instance),
    memberchk(required_crew-Required, Instance),
    length(Attributes, NumPeople),
    length(Required, NumFlights),
    length(Crew, NumFlights),
    % crew[F][P] is 1 when person P is assigned to flight F, 0 otherwise
    ( foreach(Row, Crew), param(NumPeople) do
        length(Row, NumPeople),
        Row :: 0..1
    ),
    flatten(Crew, Vars),
    % each flight has exactly the number of cabin crew it needs
    % and at least the required number of each of the other five kinds of crew member
    ( foreach(Flight, Required), foreach(Row, Crew), param(Attributes) do
        Flight = [NumCrew | Needs],
        sum(Row) #= NumCrew,
        ( for(K, 1, 5), param(Row, Attributes, Needs) do
            nth1(K, Needs, Need),
            ( foreach(Attr, Attributes), foreach(X, Row), foreach(Has, Covered), param(K) do
                nth1(K, Attr, Skill),
                Has #= X * Skill
            ),
            sum(Covered) #>= Need
        )
    ),
    % nobody attends more than one of any three consecutive flights
    Last is NumFlights - 2,
    ( for(F, 1, Last), param(Crew) do
        F1 is F + 1, F2 is F + 2,
        nth1(F, Crew, R1), nth1(F1, Crew, R2), nth1(F2, Crew, R3),
        ( foreach(A, R1), foreach(B, R2), foreach(C, R3) do
            A + B + C #=< 1
        )
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
