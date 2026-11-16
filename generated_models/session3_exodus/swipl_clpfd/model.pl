% session3_exodus: a SWI-Prolog model from DCP Rosetta.
%
% Five children at Hebrew school (Bernice, Carl, Debby, Sammy and Ted) each tell one part of the story of the Exodus
% (burning bush, captivity, Moses's youth, Passover or the Ten Commandments). Each child is a different age (three,
% five, seven, eight or ten), and each child's family came to America from a different country (Ethiopia, Kazakhstan,
% Lithuania, Morocco or Yemen). Clues: 1. Debby's family is from Lithuania. 2. The child who told the story of the
% Passover is two years older than Bernice. 3. The child whose family is from Yemen is younger than the child from
% the Ethiopian family. 4. The child from the Moroccan family is three years older than Ted. 5. Sammy is three years
% older than the child who told the story of Moses's youth. Find the age, family country and story of each child.
%
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

% Each child has a number 1..5 that appears in the lists of ages, countries and stories at the position of the
% attribute the child has. Children are indexed 0..4 in the order Bernice, Carl, Debby, Sammy, Ted.
model(_Instance, [Children, AgeI, CountryI, StoryI, AgeVal], [ages-Ages, children-Children, countries-Countries, stories-Stories]) :-
    length(Children, 5), Children ins 1..5, all_different(Children),
    length(AgeI, 5), AgeI ins 1..5, all_different(AgeI),          % position of each child's age in 3, 5, 7, 8, 10
    length(CountryI, 5), CountryI ins 1..5, all_different(CountryI),  % position of each family's country
    length(StoryI, 5), StoryI ins 1..5, all_different(StoryI),    % position of each child's part of the story
    maplist(age_value, AgeI, AgeVal),
    length(Ages, 5), Ages ins 1..5, all_different(Ages),
    length(Countries, 5), Countries ins 1..5, all_different(Countries),
    length(Stories, 5), Stories ins 1..5, all_different(Stories),
    % the list entry of each attribute holds the number of the child who has it
    maplist(lookup(Ages), AgeI, Children),
    maplist(lookup(Countries), CountryI, Children),
    maplist(lookup(Stories), StoryI, Children),
    % clue 1: Debby's family is from Lithuania (3)
    nth0(2, CountryI, DebbyCountry), DebbyCountry #= 3,
    % clue 2: the child who told the Passover story (4) is two years older than Bernice
    nth0(0, AgeVal, Bernice),
    maplist(passover_older(Bernice), StoryI, AgeVal),
    % clue 3: the child from Yemen (5) is younger than the child from Ethiopia (1)
    maplist(yemen_younger(CountryI, AgeVal), CountryI, AgeVal),
    % clue 4: the child from Morocco (4) is three years older than Ted
    nth0(4, AgeVal, Ted),
    maplist(morocco_older(Ted), CountryI, AgeVal),
    % clue 5: Sammy is three years older than the child who told the story of Moses's youth (3)
    nth0(3, AgeVal, Sammy),
    maplist(moses_younger(Sammy), StoryI, AgeVal).

age_value(I, V) :- element(I, [3, 5, 7, 8, 10], V).

lookup(List, Position, Number) :- element(Position, List, Number).

passover_older(Bernice, Story, Age) :-
    (Story #= 4) #==> (Age #= Bernice + 2).

yemen_younger(Countries, Ages, Country, Age) :-
    maplist(yemen_before_ethiopian(Country, Age), Countries, Ages).

yemen_before_ethiopian(Country, Age, OtherCountry, OtherAge) :-
    (Country #= 5 #/\ OtherCountry #= 1) #==> (Age #< OtherAge).

morocco_older(Ted, Country, Age) :-
    (Country #= 4) #==> (Age #= Ted + 3).

moses_younger(Sammy, Story, Age) :-
    (Story #= 3) #==> (Sammy #= Age + 3).

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
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
