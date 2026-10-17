load(":oplus_modules_define.bzl", "define_oplus_ddk_module")

def define_oplus_thermal_local_modules():
    define_oplus_ddk_module(
        name = "horae_shell_temp",
        srcs = native.glob([
            "**/*.h",
            "thermal/horae_shell_temp.c",
        ]),
        includes = ["."],
    )
