// SPDX-License-Identifier: GPL-2.0

#include <linux/android_kabi.h>
#include <linux/export.h>
#include <linux/poll.h>

/*
 * OOS 16.0.10.601's prebuilt rust_binder.ko was compiled against the pinned
 * Rust representation of PollCondVar's drop glue.  The newer implementation
 * still passes the same single PollCondVar pointer and performs the same
 * clear/wake/synchronize sequence, but current DWARF spells that argument as
 * &mut PollCondVar instead of Pin<&mut PollCondVar> plus the zero-sized drop
 * token.  The exported Drop entry point shares its address with the internal
 * PinnedDrop implementation, so both names must have the same version type to
 * prevent alias propagation from replacing the exported CRC.  Preserve only
 * that stock-visible type identity for symbol versioning; these rules do not
 * change code generation, object layout, or calling convention.
 */
ANDROID_KABI_TYPE_STRING(
	"_RNvXs4_NvNtNtCsdfZWD8DztAw_6kernel4sync4poll1__NtB7_11PollCondVarNtNtNtCs3o2tGsuHyou_4core3ops4drop4Drop4drop",
	"subprogram ( formal_parameter s#'core::pin::Pin<&mut kernel::sync::poll::PollCondVar>' self , formal_parameter s#kernel::init::__internal::OnlyCallFromDrop ) -> base_type void");
ANDROID_KABI_TYPE_STRING(
	"_RNvXs6_NtNtCsdfZWD8DztAw_6kernel4sync4pollNtB5_11PollCondVarNtNtB9_4init10PinnedDrop4drop",
	"subprogram ( formal_parameter s#'core::pin::Pin<&mut kernel::sync::poll::PollCondVar>' self , formal_parameter s#kernel::init::__internal::OnlyCallFromDrop ) -> base_type void");
ANDROID_KABI_TYPE_STRING(
	"s#'core::pin::Pin<&mut kernel::sync::poll::PollCondVar>'",
	"structure_type core::pin::Pin<&mut kernel::sync::poll::PollCondVar> { member pointer_type &mut kernel::sync::poll::PollCondVar { s#kernel::sync::poll::PollCondVar } __pointer accessibility(1) data_member_location(0) } byte_size(8) alignment(8)");
ANDROID_KABI_TYPE_STRING(
	"s#kernel::init::__internal::OnlyCallFromDrop",
	"structure_type kernel::init::__internal::OnlyCallFromDrop { member base_type () byte_size(0) encoding(7) __0 accessibility(3) data_member_location(0) } byte_size(0) alignment(1)");

__rust_helper
void rust_helper_poll_wait(struct file *filp, wait_queue_head_t *wait_address,
			   poll_table *p)
{
	poll_wait(filp, wait_address, p);
}
