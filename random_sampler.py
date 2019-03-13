import random
import argparse

def ternary (n):
    if n == 0:
        return '0'
    nums = []
    while n:
        n, r = divmod(n, 3)
        nums.append(str(r))
    return ''.join(reversed(nums))

def main():
    parser = argparse.ArgumentParser(description='Minterm reduction with ASP')
    parser.add_argument('out_file', metavar='O', type=str,
                        help='route for the output minterm text file')
    parser.add_argument('atoms', metavar='A', type=int,
                    help='number of atoms of the sample')
    parser.add_argument('size', metavar='S', type=int,
                    help='sample size')
    args = parser.parse_args()

    sample = []
    try:
        sample = random.sample(range(0, args.atoms**3), args.size)
    except ValueError:
        print('Sample size exceeded population size.')

    with open(args.out_file, "w") as file:
        for minterm in sample:
            file.write('%0*d\n' % (args.atoms, int(ternary(minterm))))


if __name__ == "__main__":
    main()
