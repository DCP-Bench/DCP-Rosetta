% jobs_puzzle: a clingo model from DCP Rosetta.
%
% Four people hold eight different jobs, and each person holds exactly two jobs. The jobs are chef, guard,
% nurse, clerk, police officer, teacher, actor and boxer. Clues: (1) the nurse is not a teacher, police
% officer or clerk; (2) the clerk is not the chef; (3) person 0 is not the boxer; (4) person 3 is not the
% teacher, police officer or nurse; (5) person 0, the chef and the police officer went golfing together.
% Determine which person holds which two jobs.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

person(0..3).

% each job is held by exactly one person, given as its index
1 { chef(P) : person(P) } 1.
1 { guard(P) : person(P) } 1.
1 { nurse(P) : person(P) } 1.
1 { clerk(P) : person(P) } 1.
1 { police_officer(P) : person(P) } 1.
1 { teacher(P) : person(P) } 1.
1 { actor(P) : person(P) } 1.
1 { boxer(P) : person(P) } 1.

% holds(J, P): the person P holds the job J
holds(chef,P) :- chef(P).
holds(guard,P) :- guard(P).
holds(nurse,P) :- nurse(P).
holds(clerk,P) :- clerk(P).
holds(police_officer,P) :- police_officer(P).
holds(teacher,P) :- teacher(P).
holds(actor,P) :- actor(P).
holds(boxer,P) :- boxer(P).

% each person holds exactly two jobs
:- person(P), not 2 = #count { J : holds(J,P) }.

% clue 1: the nurse is not a teacher, police officer or clerk
:- nurse(P), teacher(P).
:- nurse(P), police_officer(P).
:- nurse(P), clerk(P).

% clue 2: the clerk is not the chef
:- clerk(P), chef(P).

% clue 3: person 0 is not the boxer
:- boxer(0).

% clue 4: person 3 is not the teacher, police officer or nurse
:- teacher(3).
:- police_officer(3).
:- nurse(3).

% clue 5: person 0, the chef and the police officer are three different people
:- chef(0).
:- police_officer(0).
:- chef(P), police_officer(P).

#show chef/1.
#show guard/1.
#show nurse/1.
#show clerk/1.
#show police_officer/1.
#show teacher/1.
#show actor/1.
#show boxer/1.
