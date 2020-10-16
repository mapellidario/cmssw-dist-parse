'''Script that parses a cmssw-dist spec files and returns a requirements.txt

## Intro

This script has been written to parse WMCore clients' code dependencies
as described in https://github.com/cms-sw/cmsdist/tree/comp_gcc630 
and produce `requirements.txt`.
The end purpose is to automatically check the **python** dependencies,
gathered from pip, of a package built from a cmssw-dist spec file, 
support python3.
If a library supports python2 only it would stop the 
py2->py2&py3 migration / modernization.

## Step 1: Get the `requirements.txt` for `t0.spec` with

```bash
BASEPATH=/path/to/local/github.com/cmsdist/
SPECFILE=t0.spec
python3 parse_spec.py -d $BASEPATH -f $SPECFILE
```

`BASEPATH` and `SPECFILE` are concatenated by `os.path.join` to get the path
of the specfile that we want to examine.

The output is saved in `$PWD/requirements_$SPECFILE_auto.txt`

## Step 2: How to interpret the results.

### how to interpret the result

If a line of a `requirements.txt` contains a reference to a spec file, such
as 

```
mysqldb==1.2.4b4 # py2-mysqldb.spec
```

it means that the specific package is not downloaded directly from pip,
that a human should add the correct line to the requirements file:

* if the package is in `pypi`, just change the name.
  in the example of `mysqldb` change it to `MySQL-python`
* if the package is not in `pypi`, comment the line and check manually
  if the third-party dependency supports python2. do not rely on `caniusepython3`

## Step 3: Analysie requirements.txt

Install `caniusepython3` if you want to automatically check the 
requirements.txt files.

ACHTUNG! These results are not complete!
1. `caniusepython3` has been designed to check only libraries distributed
  through pypi.org with pip. It can not check the libraries gathered from
  sourceforge or pythonhosted.
2. `caniusepython3` fails to identify some library, such as `MySQL-python`,
  as a py2-only library, because the developers did not provide adequate
  python version trove classifiers.

## TL;DR Use this tool with care: It can not provide any definitive answers,
but it can help identifying show-stoppers.

'''

import argparse
import os
import logging
import pprint

def get_deps_spec(specdir, specfile):
    '''
    - Opens a spec files
    - Gets the list of Requirements
    - Gets the list of Requirements that start with `py2-`
    '''
    specs_py2 = [] # p5- is for cpan, perl5 dependencies
    specs_all = []
    specfile_path = os.path.join(specdir, specfile)
    logging.info(specfile_path)
    with open(specfile_path) as f:
        for line in f.readlines():
            requires_pattern = "Requires:"
            if line.strip().startswith(requires_pattern):
                deps = line[
                    line.find(requires_pattern)+len(requires_pattern):
                    ].strip()
                logging.debug(deps)
                specs = deps.split(" ")
                for spec in specs:
                    if "py2-" in spec:
                        specs_py2.append(spec.strip() + ".spec")
                    if spec.strip():
                        specs_all.append(spec.strip() + ".spec")
    return specs_py2, specs_all

deps_spec = []

def get_deps_recursive(specdir, specfile):
    '''
    - calls get_deps_spec()
    - add all the dependencies that start with `py2-` to deps_spec
    - call recursively get_deps_spec() on all the dependencies
    '''
    # first time that we call this, no specfile is saved because
    # is it the parent specfile
    specs_py2, specs_all = get_deps_spec(specdir, specfile)
    logging.info("{0} {1}".format(specfile, specs_py2))
    for spec in specs_py2:
        if spec not in deps_spec:
            deps_spec.append( spec )
    for spec in specs_all:
        get_deps_recursive(specdir, spec )
    return

def get_pipversion(specdir, specfile):
    '''
    This function is intended to parse `py2-*.spec` specfiles only
    '''
    specpath = os.path.join(specdir, specfile)
    with open(specpath) as f:
        lines = f.readlines()
        line0 = lines[0].strip()
        name_ver = []
        if "### RPM external" in line0:
            name_ver = line0[line0.find("-")+1:].split(" ")
            isin_pip = False
            for line in lines:
                if "## IMPORT build-with-pip" in line:
                    isin_pip = True
            if not isin_pip:
                return "{0}=={1} # {2} ".format(
                    name_ver[0], name_ver[1], specfile)
            else:
                return "{0}=={1}".format(
                    name_ver[0], name_ver[1])
    return None

def write_requirements(specdir, depsspec, requirements_filename):
    requirement_lines = []
    for spec in depsspec:
        line = get_pipversion(specdir, spec)
        if line:
            line += "\n"
            requirement_lines.append(line)
    with open(requirements_filename, "w") as f:
        f.writelines(requirement_lines)

def main():
    '''
    :param spec_dir: Path to base direcotry that contains the spec files
    :type spec_dir: str, required
    :param spec_file: filename of the spec file
    :type spec_file: str, required
    '''
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--spec-dir", \
    help="spec files directory path", \
    type=str, \
    required=True, \
    )
    parser.add_argument("-f","--spec-file", \
    help="spec filename", \
    type=str, \
    required=True, \
    )
    args = parser.parse_args()

    get_deps_recursive(args.spec_dir, args.spec_file)
    pprint.pprint(deps_spec)
    logging.info(len(deps_spec))

    write_requirements(args.spec_dir, deps_spec, 
      "requirements_" + args.spec_file + "_auto.txt")

if __name__ == "__main__":
    main()