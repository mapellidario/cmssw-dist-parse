# parse cmssw-dist

We focus on this branch https://github.com/cms-sw/cmsdist/tree/comp_gcc630

We would like to write a `requirements.txt` from a spec file, to check it
with `caniusepython3`.

Get the `requirements.txt` for `t0.spec` with

```bash
BASEPATH=/path/to/local/github.com/cmsdist/
SPECFILE=t0.spec
python3 parse_spec.py -d $BASEPATH -f $SPECFILE
```

`BASEPATH` and `SPECFILE` are concatenated by `os.path.join` to get the path
of the specfile that we want to examine.

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