#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild, tools
import os


class Mpg123Conan(ConanFile):
    name = "mpg123"
    version = "1.25.6"
    description = "Fast MPEG Audio decoder library"
    url = "https://github.com/sixten-hilborn/conan-mpg123"
    homepage = "https://www.mpg123.de"
    license = "LGPL 2.1"
    exports = ["LICENSE.md"]  # Packages the license for the conanfile.py
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = (
        "shared=True",
        "fPIC=True"
    )

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if self.settings.compiler == 'Visual Studio':
            self.build_requires("yasm_installer/[>=1.3]@bincrafters/stable")

    def source(self):
        source_url = "https://sourceforge.net/projects/mpg123/files/mpg123/{0}/mpg123-{0}.tar.bz2".format(self.version)
        tools.get(source_url)
        extracted_dir = self.name + "-" + self.version

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self._build_vs()
        else:
            self._build_configure()

    def _build_vs(self):
        if not self.options.shared:
            raise Exception('Only shared builds are supported for Visual Studio')
        msbuild = MSBuild(self)
        msbuild.build("{0}/ports/MSVC++/2015/win32/mpg123.sln".format(self.source_subfolder))

    def _build_configure(self):
        with tools.chdir(self.source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fPIC = self.options.fPIC
            env_build.configure()
            env_build.make()
            #env_build.make(args=['install'])

    def package(self):
        self.copy(pattern="fmt123.h", dst="include", src=os.path.join(self.source_subfolder, "src", "libmpg123"))
        self.copy(pattern="mpg123.h*", dst="include", src=os.path.join(self.source_subfolder, "src", "libmpg123"))
        if self.settings.compiler == 'Visual Studio':
            self.copy("mpg123.h", dst="include", src=os.path.join(self.source_subfolder, "ports", "MSVC++"))
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
