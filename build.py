#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bincrafters import build_template_installer, build_shared
import os


if __name__ == "__main__":
    arch = os.environ["ARCH"]

    builder = build_template_installer.get_builder()
    builder.add(settings={"os_build": build_shared.get_os(), "arch_build": arch, })
    builder.run()
