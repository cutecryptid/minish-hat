letters = ['x', '0', '1', 'z', '2', 'i', 'o', '-']
symbols = [1,2,3,4,6,7]

print('A', 'B', '\t', '|', '&', '^',  '\t', 'a', 'b')
for i in symbols:
    for j in symbols:
        print(letters[i], letters[j], '\t', (i | j), (i & j), (i ^ j), '\t', i, j)
