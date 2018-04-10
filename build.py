#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
import platform

if __name__ == "__main__":

    builder = build_template_default.get_builder()
    if platform.system() == "Windows":
        builder.items = [build for build in builder.items if build[1]["shared"]]
    builder.run()
