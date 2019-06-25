% Extract atoms from rules
base(Pr, atom(P)) :- phead(Pr,_,P).
base(Pr, atom(P)) :- nhead(Pr,_,P).
base(Pr, atom(P)) :- pbody(Pr,_,P).
base(Pr, atom(P)) :- nbody(Pr,_,P).

% Each base atom has a prime counterpart
prime(Pr, atom(Pb)) :- base(Pr, atom(Pb)).

% Each program rule is a base rule and has a prime counterpart
base(Pr, rule(R)) :- rule(Pr, R).
prime(Pr, rule(Rb)) :- base(Pr, rule(Rb)).

% There is a test rule (generated rules) for each base and prime rule
grule(Pr, base(rule(R))) :- base(Pr, rule(R)).
grule(Pr, prime(rule(R))) :- prime(Pr, rule(R)).

% Base rules use base atoms as the original rules
gphead(Pr, base(rule(R)), base(atom(A))) :- phead(Pr, R, A).
gnhead(Pr, base(rule(R)), base(atom(A))) :- nhead(Pr, R, A).
gpbody(Pr, base(rule(R)), base(atom(A))) :- pbody(Pr, R, A).
gnbody(Pr, base(rule(R)), base(atom(A))) :- nbody(Pr, R, A).

% Prime rules use prime atoms in positive parts and base atoms in negative parts
gphead(Pr, prime(rule(R)), prime(atom(A))) :- phead(Pr, R, A).
gnhead(Pr, prime(rule(R)), base(atom(A))) :- nhead(Pr, R, A).
gpbody(Pr, prime(rule(R)), prime(atom(A))) :- pbody(Pr, R, A).
gnbody(Pr, prime(rule(R)), base(atom(A))) :- nbody(Pr, R, A).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Select atom candidates for model
{ holds(base(atom(P))) } :- program(Pr), base(Pr, atom(P)).
{ holds(prime(atom(Pb))) } :- program(Pr), prime(Pr, atom(Pb)).

% If prime atom is selected then base atom must be selected too.
holds(base(atom(P))) :- holds(prime(atom(P))).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Test if selected atom candidates verify head parts of g-rules
sathead(Pr, R) :- gphead(Pr, R, L), holds(L).
sathead(Pr, R) :- gnhead(Pr, R, L), not holds(L).

% Test if selected atom doesn't unsatisfy any body part
unsatbody(Pr, R) :- gpbody(Pr, R, L), not holds(L).
unsatbody(Pr, R) :- gnbody(Pr, R, L), holds(L).

% Rule satisfaction if head is satisfied or neither head nor body are satisfied
% Classical Implication Truth Table (Head v ~Body)
satisfies(Pr, R) :- sathead(Pr,R).
satisfies(Pr, R) :- unsatbody(Pr,R).

% Forbid models that do not satisfy every g-rule
:- grule(Pr, R), not satisfies(Pr, R).

%% Run this and externally check that there is no model in Pr1 that doesn't
%% belong to Pr2 and viceversa? How to check INTERNALLY?
%% Maybe just generate the models facts and cross them
%% model(Program, NumModel, ModelAtom)
%% Checking the empty model can be tricky, just model(Program, NumModel, empty)?
%% Is this better than checking it by hand on python? Try both I GUESS.

#show holds/1.
