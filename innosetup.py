import glob
import re

import SCons.Builder
import SCons.Action
import SCons.Scanner
import SCons.Node.FS

#########################################################################

re_source = re.compile(r"source:\s*\"(.*?)\"", flags=re.I)

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
        if ("*" in pat) or ("?" in pat):
            # NOTE: files must exist
            sources += glob.glob(match.group(1))
        else:
            sources += [pat]
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
