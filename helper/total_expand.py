from itertools import product

def make_patterns(s):

    keyletters = '21'

    # Convert input string into a list so we can easily substitute letters
    seq = list(s)

    # Find indices of key letters in seq
    indices = [ i for i, c in enumerate(seq) if c in keyletters ]

    # Generate key letter combinations & place them into the list
    for t in product(keyletters, repeat=len(indices)):
        for i, c in zip(indices, t):
            seq[i] = c
        print(''.join(seq))

# Test

data = (
    '0220',
    '000000222200002',
    '0202',
    '0200022',
)

for s in data:
    print('\nInput:', s)
    make_patterns(s)
