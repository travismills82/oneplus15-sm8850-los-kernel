load(":oplus_modules_dist.bzl", "ddk_copy_to_dist_dir")
load(":thermal/oplus_thermal_local_modules.bzl", "define_oplus_thermal_local_modules")

def define_oplus_local_modules():
    define_oplus_thermal_local_modules()

    ddk_copy_to_dist_dir(
        name = "oplus_bsp_cpu",
        module_list = ["horae_shell_temp"],
    )
