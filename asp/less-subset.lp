1 { selectsol(S): solution(S) } 1.

selectimpl(X,A,V) :- sol(impl(X,A,V), S), selectsol(S).
selectimplid(X) :- selectimpl(X, _, _).
atomcount(C) :- selectsol(S), C=#count{(X,A) : sol(impl(X,A,V), S), V!=x}.
termcount(C) :- selectsol(S), C=#count{X : sol(impl(X,A,V), S)}.

#preference(p,subset){ selectimpl(X,A,V) : sol(impl(X,A,V), S), solution(S) }.

#optimize(p).

#show selectsol/1.
#show selectimpl/3.
#show selectimplid/1.
