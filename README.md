# parse cmssw-dist

We focus on this branch of cmssw-dit: https://github.com/cms-sw/cmsdist/tree/comp_gcc630

The purpose is to get a `requirements.txt` from a spec file, to check it
with `caniusepython3`.

## Produce requirements.txt

### how to run

Get the `requirements.txt` for `t0.spec` with

```bash
BASEPATH=/path/to/local/github.com/cmsdist/
SPECFILE=t0.spec
python3 parse_spec.py -d $BASEPATH -f $SPECFILE
```

`BASEPATH` and `SPECFILE` are concatenated by `os.path.join` to get the path
of the specfile that we want to examine.

### how to interpret the result

If a line of a `requirements.txt` contains a reference to a spec file, such
as 

```
mysqldb==1.2.4b4 # py2-mysqldb.spec
```

it means that the specific package is not downloaded directly from pip,
that a human should add the correct line to the requirements file:

* if the package is in `pypi`, just change the name
* if the package is not in `pypi`, comment the line and check manually
  if the third-party dependency supports python2. do not rely on `caniusepython3`

## Analyse requirements.txt

### prerequisites

Install `caniusepython3` if you want to check the requirements. It is distributed
with pip, so you can use something like:

```
python3 -m pip install --user caniusepython3
```

Or run it insude a docker
```bash
# on the host
docker run -it -v $PWD:/src python:3.8 bash

# inside the docker
python3 -m pip install caniusepython3
```

### results

`./auto` directory contains the `requirements.txt` as generated from the script,
while `./requirements` contains the manually-fixed versions of the same files.


Run `caniusepython3` on all the manually fixed requirements with

```bash
# fish shell
for i in (ls requirements/*); echo "####"; echo "-> " $i; python3 ~/.local/bin/caniusepython3 --requirements $i; end

# bash inside the docker
cd src
for i in `ls requirements/*`; do echo "####" && echo "-> " $i && caniusepython3 --requirements $i; done
```

Results are reported below. 

ACHTUNG! These results are not complete. For example, `caniusepython3` fails to identify `MySQL-python` as a py2-only library.

```plaintext
####
->  requirements/requirements_crab-devtools.spec.txt
Finding and checking dependencies ...


You need 2 projects to transition to Python 3.
Of those 2 projects, 2 have no direct dependencies blocking their transition:

  python-cjson
  python-utils
####
->  requirements/requirements_crabcache.spec.txt
Finding and checking dependencies ...

You need 1 project to transition to Python 3.
Of that 1 project, 1 has no direct dependencies blocking its transition:

  python-cjson
####
->  requirements/requirements_crabclient.spec.txt
Finding and checking dependencies ...

You need 1 project to transition to Python 3.
Of that 1 project, 1 has no direct dependencies blocking its transition:

  python-cjson
####
->  requirements/requirements_crabserver.spec.txt
Finding and checking dependencies ...

You need 1 project to transition to Python 3.
Of that 1 project, 1 has no direct dependencies blocking its transition:

  python-cjson
####
->  requirements/requirements_crabtaskworker.spec.txt
Finding and checking dependencies ...

You need 2 projects to transition to Python 3.
Of those 2 projects, 2 have no direct dependencies blocking their transition:

  python-cjson
  python-utils
####
->  requirements/requirements_dbs-client.spec.txt
Finding and checking dependencies ...

🎉  You have 0 projects blocking you from using Python 3!

####
->  requirements/requirements_dbs3-client.spec.txt
Finding and checking dependencies ...

You need 1 project to transition to Python 3.
Of that 1 project, 1 has no direct dependencies blocking its transition:

  python-cjson
####
->  requirements/requirements_dbs3-combined.spec.txt
Finding and checking dependencies ...

You need 2 projects to transition to Python 3.
Of those 2 projects, 2 have no direct dependencies blocking their transition:

  nats-client
  python-cjson
####
->  requirements/requirements_dbs3-migration.spec.txt
Finding and checking dependencies ...

You need 1 project to transition to Python 3.
Of that 1 project, 1 has no direct dependencies blocking its transition:

  python-cjson
####
->  requirements/requirements_dbs3-pycurl-client.spec.txt
Finding and checking dependencies ...

You need 1 project to transition to Python 3.
Of that 1 project, 1 has no direct dependencies blocking its transition:

  python-cjson
####
->  requirements/requirements_dbs3.spec.txt
Finding and checking dependencies ...

You need 2 projects to transition to Python 3.
Of those 2 projects, 2 have no direct dependencies blocking their transition:

  nats-client
  python-cjson
####
->  requirements/requirements_t0.spec.txt
Finding and checking dependencies ...

You need 4 projects to transition to Python 3.
Of those 4 projects, 4 have no direct dependencies blocking their transition:

  nats-client
  python-cjson
  python-utils
  restkit
####
->  requirements/requirements_t0_reqmon.spec.txt
Finding and checking dependencies ...

🎉  You have 0 projects blocking you from using Python 3!

####
->  requirements/requirements_t0wmadatasvc.spec.txt
Finding and checking dependencies ...

You need 1 project to transition to Python 3.
Of that 1 project, 1 has no direct dependencies blocking its transition:

  python-cjson

```
