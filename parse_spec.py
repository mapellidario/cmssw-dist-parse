'''Script that parses a cmssw-dist spec files and returns a requirements.txt

## Intro

This script has been written to produce requirements.txt files for
WMCore and its clients packages by recursively parsing spec files.
We considered spec files at https://github.com/cms-sw/cmsdist/tree/comp_gcc630 .
The end purpose is to automatically check if the **python** dependencies
(in particular the ones gathered from pip) 
of a package, that is built from a cmssw-dist spec file, support python3.
If a library supports python2 only it would stop the 
py2->py2&py3 migration / modernization.

## Step 1: Get the `requirements.txt` for a package, such as `t0.spec`

```bash
BASEPATH=/path/to/local/github.com/cmsdist/
SPECFILE=t0.spec
python3 parse_spec.py -d $BASEPATH -f $SPECFILE
```

`BASEPATH` and `SPECFILE` are concatenated by `os.path.join` to get the path
of the specfile that we want to examine.

The output is saved in `$PWD/requirements_$SPECFILE_auto.txt`

## Step 2: How to interpret the results.

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

Frequent manual changes:

Packages that are not downloaded from pip
* py2-docutils: sourceforge
* py2-mox: googlecode
* py2-setuptools: pythonhosted

Packages that are built form pip
* py2-cheetah: Cheetah
* py2-cjson: python-cjson
* py2-cx-oracle: cx_Oracle
* py2-funcsigs: funcsigs
* py2-jinja: Jinja2
* py2-mock: mock
* py2-mysqldb: MySQL-python
* py2-nats: nats-client
* py2-pbr: pbr
* py2-pep8: pep8
* py2-pygments: Pygments
* py2-sphinx: Sphinx
* py2-stopm: stomp.py
* py2-restkit: restkit

## Step 3: Analysie requirements.txt

Install `caniusepython3` if you want to automatically check the 
requirements.txt files.

```
python3 -m pip install --user caniusepython3

#Or run it insude a docker
# on the host
docker run -it -v $PWD:/src python:3.8 bash
# inside the docker
python3 -m pip install caniusepython3
python3 /usr/local/bin/caniusepython3 --requirements /src/requirements_t0.spec.txt
```

ACHTUNG! These results are not complete!
1. `caniusepython3` has been designed to check only libraries distributed
  through pypi.org with pip. It can not check the libraries gathered from
  sourceforge or pythonhosted.
2. `caniusepython3` fails to identify some library, such as `MySQL-python`,
  as a py2-only library, because the developers did not provide adequate
  python version trove classifiers.

## TL;DR Use this tool with care: It can not provide any definitive answers,
but it can help identifying show-stoppers for the migration.

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
    logging.info("{0} {1}".format(specfile, specs_all))
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
            logging.debug("{0} {1}".format(specfile, name_ver))
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
    help="Path of the spec's files directory (e.g. `/path/to/cmssw-dist`)", \
    type=str, \
    required=True, \
    )
    parser.add_argument("-f","--spec-file", \
    help="spec file filename (e.g. `t0.spec`)", \
    type=str, \
    required=True, \
    )
    parser.add_argument('--no-recursive', action='store_true')
    args = parser.parse_args()

    if not args.no_recursive: 
        # default behavior
        get_deps_recursive(args.spec_dir, args.spec_file)
    else:
        # when using --no-recursive argument 
        specs_py2, _ = get_deps_spec(args.spec_dir, args.spec_file)
        for spec in specs_py2:
            if spec not in deps_spec:
                deps_spec.append( spec )
    # pprint.pprint(deps_spec)
    logging.info(len(deps_spec))

    write_requirements(args.spec_dir, deps_spec, 
      "requirements_" + args.spec_file + "_auto.txt")

if __name__ == "__main__":
    main()