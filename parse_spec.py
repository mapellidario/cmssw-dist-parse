import argparse
import os
import logging
import pprint

def get_deps_spec(specdir, specfile):
    '''
    - Opens a spec files
    - Gets the list of Requirements that start with `py2-`
    '''
    specs_py2 = [] # p5- is for cpan, perl5 dependencies
    specs_all = []
    specfile_path = os.path.join(specdir, specfile)
    logging.info(specfile_path)
    with open(specfile_path) as f:
        for line in f.readlines():
            if line.strip().startswith("Requires:"):
                deps = line[line.find("Requires:")+9:].strip()
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
    calls recursively get_deps_spec()
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

if __name__ == "__main__":
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


