load(":repo_paths.bzl", "modules_label", "soc_label")
load("//build/kernel/kleaf:kernel.bzl", "ddk_module")
load(":target_variants.bzl", "get_all_variants")
load("@rules_pkg//pkg:install.bzl", "pkg_install")
load("@rules_pkg//pkg:mappings.bzl", "pkg_files", "strip_prefix")

def _define_module(target, variant):
    tv = "{}_{}".format(target, variant)

    kernel_build = soc_label("{}_base_kernel").format(tv)

    deps_load = [soc_label("all_headers")]

    ddk_module(
        name = "{}_camera_extension".format(tv),
        out = "camera_extension.ko",
        srcs = native.glob([
            "camera_extension/**/*.h",
            "camera_extension/cam_sensor_module/**/*.h",
            "camera_extension/cam_sensor_module/cam_ois/**/*.h",
            "camera_extension/cam_sensor_module/cam_ois/fw_download_interface.h",
            "camera_extension/cam_sensor_module/cam_actuator/cam_actuator_custom.c",
            "camera_extension/cam_sensor_module/cam_sensor_io/cam_sensor_io_custom.c",
            "camera_extension/cam_sensor_module/cam_sensor_io/cam_sensor_util_custom.c",
            "camera_extension/cam_sensor_module/cam_eeprom/cam_eeprom_custom.c",
            "camera_extension/cam_sensor_module/cam_sensor/cam_sensor_custom.c",
            "camera_extension/cam_sensor_module/cam_sensor/insensor_eeprom_read.c",
            "camera_extension/cam_sensor_module/cam_sensor/lafatele_oplus_cam_insensor_eeprom.c",
            "camera_extension/cam_sensor_module/cam_ois/cam_ois_custom.c",
            "camera_extension/cam_sensor_module/cam_ois/fw_download_interface.c",
            "camera_extension/cam_sensor_module/cam_ois/SEM1217S/sem1217_fw.c",
            "camera_extension/cam_sensor_module/cam_ois/BU24721/bu24721_fw.c",
            "camera_extension/cam_sensor_module/cam_ois/DW9786/dw9786_fw.c",
            "camera_extension/cam_monitor/cam_monitor.c",
            "camera_extension/cam_utils/cam_debug.c",
            "camera_extension/main.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8801/tof8801_driver.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8801/tof8801_bootloader.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8801/tof_hex_interpreter.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8801/tof8801_app0.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8806/ams_i2c.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8806/tmf8806_driver.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8806/tmf8806_hex_interpreter.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8806/tmf8806_shim.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8806/tmf8806.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof8806/tmf8806_image.c",
            "camera_extension/cam_sensor_module/cam_tof/cam_tof_common/tof_pdrv.c",
        ]),
        local_defines = ["OPLUS_FEATURE_CAMERA_COMMON", "FEATURE_ENABLE=1"],
        deps  = deps_load + [
             modules_label("qcom/opensource/camera-kernel:camera_headers"),
             modules_label("qcom/opensource/camera-kernel:camera_banner"),
             modules_label("qcom/opensource/camera-kernel:{}_camera").format(tv),
             ":camera_extension_headers",
        ],

        kernel_build = kernel_build,
    )

    pkg_files(
        name = "{}_camera_extension_dist_files".format(tv),
        srcs = [":{}_camera_extension".format(tv)],
        visibility = ["//visibility:private"],
        strip_prefix = strip_prefix.files_only(),
    )

    pkg_install(
        name = "{}_camera_extension_dist".format(tv),
        srcs = [":{}_camera_extension_dist_files".format(tv)],
        destdir = "out/target/product/{}/dlkm/lib/modules/".format(target),
    )

def define_camera_extension_modules():
    for (t, v) in get_all_variants():
        _define_module(t, v)
