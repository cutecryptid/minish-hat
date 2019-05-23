import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Minterm reduction with ASP')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help="TXT File (default: stdin)")
    args = parser.parse_args()

    try:
        fcont = args.file.read().split('\n')
    except Exception as exc:
        print("error parsing file:", args.file.name)
        print(exc)
        return 1

    dupe_count = 0
    for idx, linex in enumerate(fcont):
        for idy,liney in enumerate(fcont[idx+1:]):
            if linex == liney:
                print ("DUPE AT {0}<->{1}: {2}".format(idx+1, idx+idy+2, linex))
                dupe_count += 1

    print("OG Minterms: {0}".format(len(fcont)-dupe_count))


if __name__ == "__main__":
    main()
