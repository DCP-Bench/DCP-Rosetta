% jobs_puzzle: an ECLiPSe model from DCP Rosetta.
%
% Four people, numbered 0 to 3, hold eight different jobs: chef, guard, nurse, clerk, police officer,
% teacher, actor and boxer. Each person holds exactly two of the jobs. The clues are:
%   1. the nurse is not a teacher, police officer or clerk;
%   2. the clerk is not the chef;
%   3. person 0 is not the boxer;
%   4. person 3 is not the teacher, police officer or nurse;
%   5. person 0, the chef and the police officer went golfing together.
% The model finds which person holds which jobs.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(gfd).
:- lib(listut).

% The model reads no data fields. Each job's variable is the number of the person who holds it.
model(_Instance, Vars, [chef-Chef, guard-Guard, nurse-Nurse, clerk-Clerk,
                        police_officer-Police, teacher-Teacher, actor-Actor, boxer-Boxer]) :-
    Holders = [Chef, Guard, Nurse, Clerk, Police, Teacher, Actor, Boxer],
    Holders :: 0..3,
    % each person holds exactly two jobs: for each person, exactly two jobs have that person as holder
    ( for(P, 0, 3), foreach(Bs, Indicators), param(Holders) do
        holds_two(Holders, P, Bs)
    ),
    % clue 1: the nurse is not a teacher, police officer or clerk
    Nurse #\= Teacher,
    Nurse #\= Police,
    Nurse #\= Clerk,
    % clue 2: the clerk is not the chef
    Clerk #\= Chef,
    % clue 3: person 0 is not the boxer
    Boxer #\= 0,
    % clue 4: person 3 is not the teacher, police officer or nurse
    Teacher #\= 3,
    Police #\= 3,
    Nurse #\= 3,
    % clue 5: person 0, the chef and the police officer are three different people
    Chef #\= 0,
    Police #\= 0,
    Chef #\= Police,
    flatten(Indicators, Flags),
    append(Holders, Flags, Vars).

% holds_two(Holders, P, Bs): Bs[J] is 1 when person P holds job J, and exactly two of them are 1
holds_two(Holders, P, Bs) :-
    ( foreach(H, Holders), foreach(B, Bs), param(P) do
        (H #= P) <=> (B #= 1),
        B :: 0..1
    ),
    sum(Bs) #= 2.

:- lib(branch_and_bound).

run :- solve_model([]).

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
