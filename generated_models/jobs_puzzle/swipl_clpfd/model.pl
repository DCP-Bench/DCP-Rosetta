% jobs_puzzle: a SWI-Prolog model from DCP Rosetta.
%
% Four people (numbered 0 to 3) hold eight different jobs: chef, guard, nurse, clerk, police officer, teacher, actor
% and boxer. Each person holds exactly two jobs. Clues: (1) the nurse is not a teacher, police officer or clerk;
% (2) the clerk is not the chef; (3) person 0 is not the boxer; (4) person 3 is not the teacher, police officer or
% nurse; (5) person 0, the chef and the police officer went golfing together. Determine which person holds which
% two jobs.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% Data fields: none, the problem has no data; the model reads nothing from the instance.
% Each job's variable holds the number of the person who holds that job.
:- use_module(library(clpfd)).

model(_Instance, Vars, [actor-Actor, boxer-Boxer, chef-Chef, clerk-Clerk, guard-Guard, nurse-Nurse,
                        police_officer-Police, teacher-Teacher]) :-
    Vars = [Chef, Guard, Nurse, Clerk, Police, Teacher, Actor, Boxer],
    Vars ins 0..3,
    % each person holds exactly two of the eight jobs
    global_cardinality(Vars, [0-2, 1-2, 2-2, 3-2]),
    % clue 1: the person who is the nurse is not the teacher, the police officer or the clerk
    Nurse #\= Teacher,
    Nurse #\= Police,
    Nurse #\= Clerk,
    % clue 2: the clerk is not the chef
    Clerk #\= Chef,
    % clue 3: person 0 is not the boxer
    Boxer #\= 0,
    % clue 4: person 3 is not the teacher, the police officer or the nurse
    Teacher #\= 3,
    Police #\= 3,
    Nurse #\= 3,
    % clue 5: person 0, the chef and the police officer are three different people who went golfing together
    0 #\= Chef,
    0 #\= Police,
    Chef #\= Police.

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).

solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
