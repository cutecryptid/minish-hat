program(1).
rule(1, 1). phead(1, 1, 'q'). nhead(1, 1, 'q'). nbody(1, 1, 'p').
rule(1, 2). pbody(1, 2, 'q'). nbody(1, 2, 'p').
rule(1, 3). phead(1, 3, 'p'). nhead(1, 3, 'p'). nbody(1, 3, 'q').
rule(1, 4). phead(1, 4, 'q'). phead(1, 4, 'p'). nhead(1, 4, 'q'). nhead(1, 4, 'p').
rule(1, 5). phead(1, 5, 'p'). nhead(1, 5, 'p'). pbody(1, 5, 'q').

program(2).
rule(2, 1). phead(2, 1, 'p'). pbody(2, 1, 'q').
rule(2, 2). phead(2, 2, 'p'). nhead(2, 2, 'p').
