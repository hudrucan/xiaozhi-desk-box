// SPDX-License-Identifier: GPL-2.0+
/* Backport of U-Boot's kaslrseed command for the Rockchip v2017.09 tree. */

#include <common.h>
#include <command.h>
#include <dm.h>
#include <rng.h>
#include <fdt_support.h>

static int do_kaslr_seed(cmd_tbl_t *cmdtp, int flag, int argc,
			 char * const argv[])
{
	struct udevice *dev;
	u64 seed;
	int nodeoffset;
	int ret;

	if (uclass_get_device(UCLASS_RNG, 0, &dev) || !dev) {
		printf("No RNG device\n");
		return CMD_RET_FAILURE;
	}

	ret = dm_rng_read(dev, &seed, sizeof(seed));
	if (ret) {
		printf("Reading RNG failed: %d\n", ret);
		return CMD_RET_FAILURE;
	}

	if (!working_fdt) {
		printf("No FDT memory address configured\n");
		return CMD_RET_FAILURE;
	}

	ret = fdt_check_header(working_fdt);
	if (ret < 0) {
		printf("Invalid working FDT: %s\n", fdt_strerror(ret));
		return CMD_RET_FAILURE;
	}

	nodeoffset = fdt_find_or_add_subnode(working_fdt, 0, "chosen");
	if (nodeoffset < 0) {
		printf("Cannot find or create /chosen: %s\n",
		       fdt_strerror(nodeoffset));
		return CMD_RET_FAILURE;
	}

	ret = fdt_setprop(working_fdt, nodeoffset, "kaslr-seed", &seed,
			  sizeof(seed));
	if (ret < 0) {
		printf("Cannot set /chosen/kaslr-seed: %s\n", fdt_strerror(ret));
		return CMD_RET_FAILURE;
	}

	return CMD_RET_SUCCESS;
}

U_BOOT_CMD(
	kaslrseed, 1, 0, do_kaslr_seed,
	"set /chosen/kaslr-seed from the hardware RNG",
	""
);
