# Minish HAT: Here-And-There Logic Program and Theories minimization in ASP

## Usage
Run ```python minish-hat.py INPUT_FILE```. Python 3.x and clingo 5.x.
Asprin is optional but recommended, as it is just used for complex minimization modes.

The input file must contain the terms of the function to minimize either in their ternary representation, one term per line
or in a logic program format without nesting. See the samples at the provided input folder for reference.
In ternary representation, the terms should be either the countermodels of the logic program/theory or the program rules translated to labels (with ```z=not 2``` and ```o=not 0```).

The script generates the prime implicates in Python and leverages ASP to do the mincover for all of the generated prime implicates. This behaviour can be altered to let python extract the Essential Implicates first and use ASP to determine the remaining minimal coverage by using the parameter ```-hc/--hybridcover```.

Only a single minimal solution will be specified, to show all of the possible minimal solutions, use the ```--all``` parameter. Minimization method can be specified through the ```-m / --minmode``` parameter.

### Minish-HAT or Minish-Countermodels?
Minish-HAT is a combined version of the two approaches (aggregates and countermodels)
that performs better than Minish-Countermodels in the average case when there are
rule representations containing "not 0"s, "not 2"s and "don't care"s. In the best case
it can perform an order of magnitude better, while in the worst case it has a bit
of overhead time because it's not as optimized as Minish-Countermodels when dealing
with a pure countermodel input (no aggregates in rules).

It is recommended to use Minish-HAT, but you can check if for your problem Minish-Countermodels
does better.

### Usage Output
```
usage: minish-hat.py [-h] [-hc] [-a] [-m {atoms,terms}] [-t] [-te] [-ts] [-ct]
                     [file]

Here-And-There Logic Program and Theories minimization in ASP

positional arguments:
  file                  TXT File (default: stdin)

optional arguments:
  -h, --help            show this help message and exit
  -hc, --hybridcover    Perform mincover in two steps python-ASP instead of
                        all ASP
  -a, --all             Show all minimal solutions instead of a single one
  -m {atoms,terms}, --minmode {atoms,terms}
                        Minimization method, less atoms by default
  -t, --time            Show time measures for the different stages
  -te, --testeq         Perform Strong Equivalence tests on minimal results
  -ts, --testsub        Perform Subsumption tests on minimal results
  -ct, --covertable     Prints Prime Implicate Cover table
```

## TO DO
* Only simple minimizations by atoms and terms are supported, no asprin option to combine or minimal subset yet.
* Merge Countermodels version into main program (Countermodels version doesn't support tests nor Cover Table options)
