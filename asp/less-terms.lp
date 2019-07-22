1 { selectsol(S): solution(S) } 1.

selectimpl(X,A,V) :- sol(impl(X,A,V), S), selectsol(S).
selectimplid(X) :- selectimpl(X, _, _).
termcount(C) :- selectsol(S), C=#count{X : sol(impl(X,A,V), S)}.

#minimize { C : termcount(C) }.

#show selectsol/1.
#show selectimpl/3.
#show selectimplid/1.
