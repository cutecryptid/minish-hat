#include <incmode>.

%% t = 0
#program base.
minid(Z, 0) :- uprimplcvr(_, Z).
pimplid(X, 0) :- uprimplid(X).
pimplcvr(X, Z, 0) :- uprimplcvr(X, Z).

%% t > 0
#program step(t).
pimplid(X, t) :- pimplid(X, t-1), not essnimplid(X, t-1), not discardimplid(X, t-1).
pimplcvr(X, Z, t) :- uprimplcvr(X, Z), pimplid(X, t).
minid(Z, t) :- minid(Z, t-1), not usedminid(Z, t-1).

%% t >= 0
#program check(t).
mincount(Z, C, t) :- minid(Z, t), C=#count{X:pimplcvr(X, Z, t)}.
essnimplid(X, t) :- pimplcvr(X, Z, t), mincount(Z, 1, t).
usedminid(Z, t) :- essnimplid(X, t), uprimplcvr(X, Z).
usedminid(Z, t) :- usedminid(Z, t-1).
discardimplid(X, t) :- pimplcvr(X, Z, t), usedminid(Z, t).
discardimplid(X, t) :- discardimplid(X, t-1).

:- query(t), essnimplid(X, t).

discardimplid(X) :- discardimplid(X, t).

uncover(t) :-  uprimplid(X), not discardimplid(X, t).
fullcover(t) :- not uncover(t), query(t).

essnimplid(X) :- essnimplid(X, t).
essnimplcvr(X, Z) :- essnimplid(X), uprimplcvr(X, Z).
essnimpl(X, A, V) :- essnimplid(X), uprimpl(X, A, V).

leftimplid(X) :- uprimplid(X), not essnimplid(X).
leftimplcvr(X, Z) :- leftimplid(X), uprimplcvr(X, Z).
leftimpl(X, A, V) :- leftimplid(X), uprimpl(X, A, V).

#show fullcover/1.

#show essnimplid/1.
#show essnimplcvr/2.
#show essnimpl/3.

#show leftimplid/1.
#show leftimplcvr/2.
#show leftimpl/3.
