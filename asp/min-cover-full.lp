minid(Z) :- covers(_,Z).
implid(X) :- leftid(X).

1 { selectid(X) : implid(X) }.

coveredminid(Z) :- selectid(X), covers(X,Z).
uncoveredminid(Z) :- minid(Z), not coveredminid(Z).

overlapcount(X,Y,C) :- selectid(X), selectid(Y), X<Y,
                          C=#count{ Z : covers(X,Z), covers(Y,Z) }.
covercount(X,C) :- selectid(X), C=#count{ Z: covers(X,Z) }.

:- uncoveredminid(Z).
:- overlapcount(X,Y,C), covercount(X,C).
:- overlapcount(X,Y,C), covercount(Y,C).

implidcount(C) :- C=#count{ X: selectid(X) }.

#minimize { C : implidcount(C)  }.

#show selectid/1.
