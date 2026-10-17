# SPDX-License-Identifier: GPL-2.0
vendor := $(src)

ifeq ($(CONFIG_ARCH_CANOE),y)
DTC_INCLUDE += \
	$(srctree)/../vendor/oneplus/sm8850-modules/qcom/opensource/audio-kernel/include \
	$(srctree)/../vendor/oneplus/sm8850-modules/qcom/opensource/camera-kernel \
	$(srctree)/../vendor/oneplus/sm8850-modules/qcom/opensource/synx-kernel
endif

ifneq "$(wildcard $(vendor)/qcom)" ""
#OPLUS_DTS_OVERLAY start
	subdir-y += qcom
#OPLUS_DTS_OVERLAY end
endif
#OPLUS_DTS_OVERLAY start
subdir-y += oplus
#OPLUS_DTS_OVERLAY end

# Silence all DTC warnings by default
DTC_FLAGS += -q
