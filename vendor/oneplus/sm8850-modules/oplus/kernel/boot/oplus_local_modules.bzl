load(":repo_paths.bzl", "soc_label")

load(":oplus_modules_define.bzl", "define_oplus_ddk_module", "oplus_ddk_get_target", "oplus_ddk_get_variant", "bazel_support_platform")
load(":oplus_modules_dist.bzl", "ddk_copy_to_dist_dir")

def define_oplus_local_modules():
    target = oplus_ddk_get_target()
    variant  = oplus_ddk_get_variant()
    kernel_build_variant = "{}_{}".format(target, variant)

    define_oplus_ddk_module(
        name = "saupwk",
        srcs = native.glob([
            "cmdline_parser/saupwk.c",
        ]),
        includes = ["include"],
    )
    define_oplus_ddk_module(
        name = "oplusboot",
        srcs = native.glob([
            "cmdline_parser/oplusboot.c",
        ]),
        includes = ["include"],
    )
    define_oplus_ddk_module(
        name = "oplus_ftm_mode",
        srcs = native.glob([
            "cmdline_parser/oplus_ftm_mode.c",
        ]),
        includes = ["include"],
    )
    define_oplus_ddk_module(
        name = "oplus_charger_present",
        srcs = native.glob([
            "cmdline_parser/oplus_charger_present.c",
        ]),
        includes = ["include"],
    )
    define_oplus_ddk_module(
        name = "buildvariant",
        srcs = native.glob([
            "cmdline_parser/buildvariant.c",
        ]),
        includes = ["include"],
    )
    define_oplus_ddk_module(
        name = "cdt_integrity",
        srcs = native.glob([
            "cmdline_parser/cdt_integrity.c",
        ]),
        includes = ["include"],
    )
    define_oplus_ddk_module(
        name = "oplus_bootargs",
        srcs = native.glob([
            "cmdline_parser/oplus_bootargs.c",
        ]),
        includes = ["include"],
    )
    define_oplus_ddk_module(
        name = "oplus_bsp_bootmode",
        srcs = native.glob([
            "bootmode/boot_mode.c",
        ]),
        ko_deps = [
            ":oplus_ftm_mode",
            ":oplusboot",
            ":oplus_charger_present",
        ],
        includes = ["include"],
    )
    define_oplus_ddk_module(
        name = "oplus_bsp_bootloader_log",
        srcs = native.glob([
            "bootloader_log/bootloader_log.c",
        ]),
        includes = ["include"],
    )

    if bazel_support_platform == "qcom" :
        ko_deps = [
                ":buildvariant",
                ":oplusboot",
                soc_label("{}/drivers/soc/qcom/smem").format(kernel_build_variant),
        ]
        copts = ["-DCONFIG_QCOM_SMEM"]
    else :
        ko_deps = [
                ":buildvariant",
                ":oplusboot",
        ]
        copts = []

    define_oplus_ddk_module(
        name = "oplus_bsp_boot_projectinfo",
        srcs = native.glob([
            "include/oplus_project.h",
        ]),

        ko_deps = ko_deps,

        conditional_srcs = {
            "CONFIG_OPLUS_DDK_MTK": {
                True: ["oplus_projectinfo/mtk/oplus_project.c"],
                False: ["oplus_projectinfo/qcom/oplus_project.c"],
            }
        },
        conditional_defines = {
            "mtk":  ["CONFIG_OPLUS_SYSTEM_KERNEL_MTK"],
            "qcom": ["CONFIG_OPLUS_SYSTEM_KERNEL_QCOM"],
        },
        copts = copts,
        includes = ["include"],
    )

    ddk_copy_to_dist_dir(
        name = "oplus_bsp_boot",
        module_list = [
            "saupwk",
            "oplusboot",
            "oplus_ftm_mode",
            "oplus_charger_present",
            "buildvariant",
            "cdt_integrity",
            "oplus_bsp_bootmode",
            "oplus_bsp_bootloader_log",
            "oplus_bsp_boot_projectinfo",
        ],
    )
