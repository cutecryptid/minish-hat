base(atom(P)) :- phead(_,_,P).
base(atom(P)) :- nhead(_,_,P).
base(atom(P)) :- pbody(_,_,P).
base(atom(P)) :- nbody(_,_,P).

phead(R, P) :- phead(_,R,P).
nhead(R, P) :- nhead(_,R,P).
pbody(R, P) :- pbody(_,R,P).
nbody(R, P) :- nbody(_,R,P).

prime(atom(Pb)) :- base(atom(Pb)).

{ holds(base(atom(P))) } :- base(atom(P)).
{ holds(prime(atom(Pb))) } :- prime(atom(Pb)).

holds(base(atom(P))) :- holds(prime(atom(P))).

base(rule(R)) :- rule(Pr, R).
prime(rule(Rb)) :- base(rule(Rb)).

xrule(base(rule(R))) :- base(rule(R)).
xrule(prime(rule(R))) :- prime(rule(R)).

xphead(base(rule(R)), base(atom(A))) :- phead(R, A).
xnhead(base(rule(R)), base(atom(A))) :- nhead(R, A).
xpbody(base(rule(R)), base(atom(A))) :- pbody(R, A).
xnbody(base(rule(R)), base(atom(A))) :- nbody(R, A).

xphead(prime(rule(Rb)), prime(atom(Ab))) :-
  xphead(base(rule(R)), base(atom(A))), prime(atom(Ab)), prime(rule(Rb)).
xnhead(prime(rule(Rb)), base(atom(A))) :-
  xnhead(base(rule(R)), base(atom(A))), prime(rule(Rb)).
xpbody(prime(rule(Rb)), prime(atom(Ab))) :-
  xpbody(base(rule(R)), base(atom(A))), prime(atom(Ab)), prime(rule(Rb)).
xnbody(prime(rule(Rb)), base(atom(A))) :-
  xnhead(base(rule(R)), base(atom(A))), prime(rule(Rb)).

% TODO: Check the holds that satisfy all of the xrule using xphead, xnhead, etc.
% Head is OR-checked so a single correct value satisfies head
% Body is AND-checked so every value must be correct for holds to satisfy the body

sathead(R) :- xphead(R, L), holds(L).
sathead(R) :- xnhead(R, L), not holds(L).

unsatbody(R) :- xpbody(R, L), not holds(L).
unsatbody(R) :- xnbody(R, L), holds(L).

satbody(R) :- xrule(R), not unsatbody(R).

satisfies(R) :- xrule(R), sathead(R).
satisfies(R) :- xrule(R), satbody(R).

:- xrule(R), not satisfies(R).

#show holds/1.
