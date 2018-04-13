#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_shared

if __name__ == "__main__":
    builder = build_shared.get_builder()
    builder.add_common_builds(shared_option_name="mpg123:shared", pure_c=True, dll_with_static_runtime=True)

    builder.run()
