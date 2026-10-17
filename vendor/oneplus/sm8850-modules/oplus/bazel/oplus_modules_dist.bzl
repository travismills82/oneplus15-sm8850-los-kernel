load(":oplus_modules_variant.bzl",
    "bazel_support_target",
    "bazel_support_variant"
)

load(":oplus_modules_define.bzl", "oplus_ddk_get_oplus_features")
load("@rules_pkg//pkg:install.bzl", "pkg_install")
load("@rules_pkg//pkg:mappings.bzl", "pkg_files", "strip_prefix")

def ddk_copy_to_dist_dir(
        name = None,
        module_list = [],
        conditional_builds = None):

    data = []

    if name == None:
        name = "ddk_oplus_default"

    # Handle conditionally compiled code when compilation conditions exist
    if conditional_builds:
        # Get variables passed from environment variables; oplus_feature_list is a dictionary.
        oplus_feature_list = oplus_ddk_get_oplus_features()
        for module in module_list:
            # When there are compilation conditions for this module,
            # map the compilation conditions to the environment variable settings one-to-one.
            # Only compile if all conditions are met
            conditional_build = conditional_builds.get(module, None)
            if conditional_build:
                skip = 0
                for k in conditional_build:
                    v = conditional_build[k]
                    sv1 = str(v).upper()
                    sv2 = str(oplus_feature_list.get(k, 'foo')).upper()
                    if sv1 != sv2:
                        skip += 1
                if skip > 0:
                    print("Remove: compilation conditions are not met in %s" % module)
                    print("Settings:", oplus_feature_list)
                    print("Conditionals:", conditional_build)
                    continue
                else:
                    print("Added: compilation conditions are met in %s" % module)
                    data.append(":{}".format(module))
            else:
                data.append(":{}".format(module))
    else:
        # raw pass: modules has no conditional compilation options
        for module in module_list:
            data.append(":{}".format(module))

    if len(data) == 0:
        return

    for target in bazel_support_target:
        for variant in bazel_support_variant:
            stem = "{}_{}_{}".format(target, variant, name)

            pkg_files(
                name = "{}_dist_files".format(stem),
                srcs = data,
                visibility = ["//visibility:private"],
                strip_prefix = strip_prefix.files_only(),
            )

            pkg_install(
                name = "{}_dist".format(stem),
                srcs = [":{}_dist_files".format(stem)],
                destdir = "out/msm-kernel-{}-{}/dist".format(target, variant),
            )
