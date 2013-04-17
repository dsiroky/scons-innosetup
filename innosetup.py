import glob
import re
import os

import SCons.Builder
import SCons.Action
import SCons.Scanner
import SCons.Node.FS

#########################################################################

re_source = re.compile(r"source:\s*\"(.*?)\"(.*)", flags=re.I)

#########################################################################

def recursesubdirs(pat):
    files = []
    for item in glob.glob(pat):
        for dn, subdirs, dfiles in os.walk(item):
            for fn in dfiles:
                fn = os.path.join(dn, fn)
                files.append(fn)
    return files

#########################################################################

def inno_scanner(node, env, path):
    # replace constants
    contents = node.get_text_contents()
    for idef in env["ISCCDEFINES"]:
        key, value = idef.split("=")
        value = value.strip("\"")
        contents = contents.replace("{#%s}" % key, value)
    # get sources
    sources = []
    for match in re_source.finditer(contents):
        pat = match.group(1)
        if "recursesubdirs" in match.group(2):
            files = recursesubdirs(pat)
        else:
            files = glob.glob(pat)
            if len(files) == 0:
                sources += [pat]
            else:
                sources += files
    return sources

#########################################################################

def inno_generator(source, target, env, for_signature):
    INNO_DEFINES=" ".join(["/D"+define for define in env["ISCCDEFINES"]])
    return ('$ISCC %(DEFINES)s /O"$TARGET.dir" /F"$TARGET.filebase" $ISCCOPTIONS $SOURCE' %
        {
            "DEFINES":INNO_DEFINES,
        })

#########################################################################

def generate(env,**kw):
    env["ISCC"]="iscc"
    env["ISCCOPTIONS"]="/q"
    env["ISCCDEFINES"]=[]
    env["ISCCSUFFIX"]=".iss"
    env["ISCCEXESUFFIX"]=".exe"

    InnoScanner = SCons.Scanner.Scanner(name="inno_scanner",
                                        function=inno_scanner,
                                        skeys=[".iss"])

    InnoAction = SCons.Action.CommandGeneratorAction(inno_generator,
                                                  {"cmdstr":"$ISCCCOMSTR"})

    InnoBuilder = SCons.Builder.Builder(
        action=InnoAction,
        src_suffix="$ISCCSUFFIX",
        suffix="$ISCCEXESUFFIX",
        single_source=True,
        source_scanner=InnoScanner
      )

    env.Append(BUILDERS={"InnoInstaller": InnoBuilder},
                SCANNERS=InnoScanner)

#########################################################################

def exists(env):
    return env.Detect("iscc")
