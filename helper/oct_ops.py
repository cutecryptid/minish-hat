def count_set_bits(octx):
    count = 0
    while octx:
        count += 1 if (octx & 7 > 0) else 0
        octx >>= 3
    return count

def is_valid_adj(octx):
    count = 0
    while octx:
        count += 1 if (octx & 7 == 5) else 0
        octx >>= 3
    return True if not count else False
