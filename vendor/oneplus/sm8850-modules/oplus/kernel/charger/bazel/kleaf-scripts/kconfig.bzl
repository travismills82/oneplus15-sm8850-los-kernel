load("//build/kernel/kleaf:hermetic_tools.bzl", "hermetic_genrule")

def define_oplus_chg_kconfig(name):
    hermetic_genrule(
        name = "kconfig.{}.generated".format(name),
        srcs = native.glob(["**/Kconfig*"]),
        outs = ["Kconfig.ext"],
        cmd = "KCONFIG_EXT_PREFIX={}/ $(location kleaf-scripts/flatten_kconfig.sh) $(location Kconfig.ddk) >$@".format(native.package_name()),
        tools = ["kleaf-scripts/flatten_kconfig.sh"],
    )
