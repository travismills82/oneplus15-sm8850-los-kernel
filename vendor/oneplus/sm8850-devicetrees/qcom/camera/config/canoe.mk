ifdef OPLUS_USE_QCOM_DTBO
dtbo-$(CONFIG_ARCH_CANOE)   += canoe-camera.dtbo \
	alor-interposer-camera.dtbo \
	alor-interposer-camera-sensor-cdp.dtbo \
	alor-interposer-camera-sensor-mtp.dtbo \
	alor-interposer-camera-sensor-qrd.dtbo \
	alor-camera.dtbo \
	whale-camera.dtbo
dtbo-$(CONFIG_ARCH_CANOE)   += canoe-camera-v2.dtbo \
	alor-interposer-camera-v2.dtbo \
	canoe-camera-sensor-mtp.dtbo \
	canoe-camera-sensor-cdp.dtbo \
	canoe-camera-sensor-qrd.dtbo \
	canoe-camera-sensor-hdk.dtbo \
	canoe-camera-sensor-rumi.dtbo \
	alor-camera-sensor-mtp.dtbo \
	alor-camera-sensor-cdp.dtbo \
	alor-camera-sensor-qrd.dtbo \
	alor-camera-sensor-mtp-peach.dtbo \
	alor-camera-sensor-rcm-peach.dtbo
else
dtbo-$(CONFIG_ARCH_CANOE) += canoe-camera.dtbo \
	alor-camera.dtbo \
	whale-camera.dtbo \
	alor-camera-sensor-cdp.dtbo \
	alor-camera-sensor-qrd.dtbo

dtbo-$(CONFIG_ARCH_CANOE)   += canoe-camera-v2.dtbo \
	alor-interposer-camera-v2.dtbo

dtbo-$(CONFIG_ARCH_CANOE)   += oplus/infiniti-camera-sensor-mtp-preT0.dtbo       \
                               oplus/infiniti-camera-sensor-mtp-T0.dtbo \
	oplus/fairlady-camera-sensor-mtp-EVB.dtbo \
	oplus/fairlady-camera-sensor-mtp-EVB-export.dtbo \
	oplus/macan-camera-sensor-mtp-T0.dtbo \
	oplus/macanEx-camera-sensor-mtp-T0.dtbo
endif

dtbo-$(CONFIG_ARCH_CHORA) += chora-camera.dtbo \
	chora-camera-sensor-mtp.dtbo \
	chora-camera-sensor-qrd.dtbo \
	chora-camera-sensor-cdp.dtbo \
	chora-camera-sensor-rcm.dtbo
dtbo-$(CONFIG_ARCH_BOURTZI) += bourtzi-camera.dtbo \
	bourtzi-camera-sensor-mtp.dtbo \
	bourtzi-camera-sensor-qrd.dtbo \
	bourtzi-camera-sensor-cdp.dtbo \
	bourtzi-camera-sensor-rcm.dtbo
