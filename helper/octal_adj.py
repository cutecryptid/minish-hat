import sys

data = [
    ('0zo','1zo'), # TOTAL ADJ -> zzo
    ('0zo','1z-'), # PARTIAL ADJ -> zzo
    ('1zo','1z-'), # COMPAT ONLY
    ('000','020'), # NOT-ADJ
    ('0z0','020'), # NOT-ADJ
    ('0z1','021'), # NOT-ADJ
    ('0z0','1z1'), # NOT-ADJ, Multiple Adj positions
    ('0o0','0z0'), # TOTAL ADJ -> 0-0
    ('o-o','z--')
]

def label_to_octal(label):
    translation = {
        'x' : '0',
        '0' : '1',
        '1' : '2',
        '2' : '4',
        'z' : '3',
        'o' : '6',
        '-' : '7',
        'i' : '5'
    }
    octalstr = ""
    for a in label:
        octalstr += translation[a]
    return int(octalstr, 8)

def octal_to_label(octx):
        translation = {
            '1' : '0',
            '2' : '1',
            '4' : '2',
            '3' : 'z',
            '6' : 'o',
            '7' : '-',
            '5' : 'i',
            '0' : 'x'
        }
        label = ""
        for a in oct(octx)[2:]:
            label += translation[a]
        return label

def build_mask(a, b, or_ret, and_ret):
    mask = 0
    comp_mask = 0
    pos = 0
    while a or b or and_ret:
        ret = 0
        if (and_ret & 7 == 0) and ((or_ret & 7) in (3,6)):
            ret = 7
        elif (and_ret & 7 == 2) and a&7 != b&7 and a&7 in (3,6) and b&7 in (3,6):
            ret = 7
        mask += ret * (8 ** pos)
        comp_mask += (7-ret) * (8 ** pos)
        pos += 1
        and_ret >>= 3
        or_ret >>= 3
        a >>= 3
        b >>= 3
    return (mask,comp_mask)

def count(mask, needle):
    count = 0
    while mask:
        count += 1 if (mask & 7 == needle) else 0
        mask >>= 3
    return count

def check_partial_adj(p0, p1):
    or_ret = p0 | p1
    and_ret = p0 & p1
    xor_ret = p0 ^ p1
    mask = 0
    comp_mask = 0
    pos = 0
    while a or b or and_ret:
        ret = 0
        if (and_ret & 7 == 0) and ((or_ret & 7) in (3,6)):
            ret = 7
        elif (and_ret & 7 == 2) and a&7 != b&7 and a&7 in (3,6) and b&7 in (3,6):
            ret = 7
        mask += ret * (8 ** pos)
        comp_mask += (7-ret) * (8 ** pos)
        pos += 1
        and_ret >>= 3
        or_ret >>= 3
        a >>= 3
        b >>= 3
    count = 0
    masked_xor = xor_ret & comp_mask
    while mask:
        count += 1 if (mask & 7 == 7) else 0
        mask >>= 3
    return mask > 0 and adj_pos_count == 1 and masked_xor != 0

for pair in data:
    p0, p1 = label_to_octal(pair[0]), label_to_octal(pair[1])
    or_ret = p0 | p1
    and_ret = p0 & p1
    xor_ret = p0 ^ p1
    print(pair[0], pair[1])
    print("OR", octal_to_label(or_ret), oct(or_ret))
    print("AND", octal_to_label(and_ret), oct(and_ret))
    print("XOR", octal_to_label(xor_ret), oct(xor_ret))
    mask, comp_mask = build_mask(p0, p1, or_ret, and_ret)
    print("MASKS", oct(mask), oct(comp_mask))
    adj_pos_count = count(mask, 7)
    masked_xor = xor_ret & comp_mask
    print("MASKED XOR", oct(masked_xor))
    if mask > 0 and adj_pos_count == 1:
        if masked_xor == 0:
            print("TOTALLY ADJACENT")
            res = or_ret
        else:
            print("PARTIALLY ADJACENT")
            res = ((or_ret & mask) | (and_ret & comp_mask))
            #TODO:  If partial, expand and add to next step
            #       See if we can add some heuristic for comparison
        print("RESULT", octal_to_label(res), oct(res))
    else:
        print("INCOMPATIBLE")
    print()

# Primer barrido para descomponer los parcialmente adyacentes
# (Se añaden al mismo step?)
# Segundo barrido para emparejar, ya teniendo en cuenta peso y adjval
# Marcar como viene siendo habitual
# Marca de expanded, marca de used
