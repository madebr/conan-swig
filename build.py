#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bincrafters import build_template_installer, build_shared
import os


if __name__ == "__main__":
    arch = os.environ["ARCH"]

    builder = build_template_installer.get_builder()

    builder.add_common_builds()
    builds = builder.items
    compiler_props = {k: v for (k, v, ) in builds[0].settings.items() if k.startswith("compiler")}
    builder.items = []

    builder.add(settings={"os_build": build_shared.get_os(), "arch_build": arch, "os": build_shared.get_os(), "arch": arch, **compiler_props})
    builder.run()
