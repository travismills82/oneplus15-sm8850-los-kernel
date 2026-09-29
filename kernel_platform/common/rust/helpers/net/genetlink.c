// SPDX-License-Identifier: GPL-2.0

/*
 * Copyright (C) 2026 Google LLC.
 */

#include <linux/android_kabi.h>
#include <net/genetlink.h>

/*
 * Keep the Rust view of struct net opaque for KMI versioning.  Adding the
 * generic netlink bindings makes bindgen emit the complete structure, even
 * though the existing Rust interfaces only carry it behind opaque pointers.
 * Expanding it would therefore change the CRCs of unrelated Rust exports
 * without changing their binary calling convention.
 *
 * This is the exact representation used by the qualified OOS 16.0.10.601
 * kernel and its stock rust_binder.ko.
 */
ANDROID_KABI_TYPE_STRING(
	"s#bindings::bindings_raw::net",
	"structure_type bindings::bindings_raw::net { member array_type[0] { base_type u8 byte_size(1) encoding(7) } _unused accessibility(3) data_member_location(0) } byte_size(0) alignment(1)");

#ifdef CONFIG_NET

__rust_helper struct sk_buff *rust_helper_genlmsg_new(size_t payload, gfp_t flags)
{
	return genlmsg_new(payload, flags);
}

__rust_helper
int rust_helper_genlmsg_multicast(const struct genl_family *family,
				  struct sk_buff *skb, u32 portid,
				  unsigned int group, gfp_t flags)
{
	return genlmsg_multicast(family, skb, portid, group, flags);
}

__rust_helper void rust_helper_genlmsg_cancel(struct sk_buff *skb, void *hdr)
{
	genlmsg_cancel(skb, hdr);
}

__rust_helper void rust_helper_genlmsg_end(struct sk_buff *skb, void *hdr)
{
	genlmsg_end(skb, hdr);
}

__rust_helper void rust_helper_nlmsg_free(struct sk_buff *skb)
{
	nlmsg_free(skb);
}

__rust_helper
int rust_helper_genl_has_listeners(const struct genl_family *family,
				   struct net *net, unsigned int group)
{
	return genl_has_listeners(family, net, group);
}

#endif
