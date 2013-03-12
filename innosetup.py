import SCons.Builder
import SCons.Action

def inno_generator(source, target, env, for_signature):
    INNO_DEFINES=" ".join(["/D"+define for define in env["ISCCDEFINES"]])
    return ('$ISCC %(DEFINES)s /O"$TARGET.dir" /F"$TARGET.filebase" $ISCCOPTIONS $SOURCE' %
        {
            "DEFINES":INNO_DEFINES,
        })

def generate(env,**kw):
    env["ISCC"]="iscc"
    env["ISCCOPTIONS"]="/q"
    env["ISCCDEFINES"]=[]
    env["ISCCSUFFIX"]=".iss"
    env["ISCCEXESUFFIX"]=".exe"

    InnoAction = SCons.Action.CommandGeneratorAction(inno_generator,
                                                  {"cmdstr":"$ISCCCOMSTR"})

    inno_builder = SCons.Builder.Builder(
        action=InnoAction,
        src_suffix="$ISCSUFFIX",
        suffix="$ISCCEXESUFFIX",
        single_source=True
      )

    env.Append(BUILDERS={
        "InnoInstaller": inno_builder
      })

def exists(env):
    return env.Detect("iscc")
