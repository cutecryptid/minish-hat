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
    parser.add_argument('atoms', metavar='A', type=int,
                    help='number of atoms of the sample')
    parser.add_argument('size', metavar='S', type=int,
                    help='sample size')
    parser.add_argument('-o', '--out', metavar='O', type=str,
                        help='optional route for the output minterm text file')
    args = parser.parse_args()

    if args.out != None:
        out_file = args.out
    else:
        out_file = "./input/rnsample_{0}_{1}.txt".format(args.atoms, args.size)

    sample = []
    try:
        rn = range(0, 3**args.atoms)
        sample = sorted(random.sample(rn, args.size))

        with open(out_file, "w") as file:
            for minterm in sample:
                file.write('%0*d\n' % (args.atoms, int(ternary(minterm))))
    except ValueError:
        print('Sample size exceeded population size.')


if __name__ == "__main__":
    main()
