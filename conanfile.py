#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class Mpg123Conan(ConanFile):
    name = "mpg123"
    version = "1.25.6"
    description = "Fast MPEG Audio decoder library"
    url = "https://github.com/sixten-hilborn/conan-mpg123"
    homepage = "https://www.mpg123.de"

    # Indicates License type of the packaged library
    license = "LGPL 2.1"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = (
        "shared=True",
        "fPIC=True"
    )

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    # Use version ranges for dependencies unless there's a reason not to
    # Update 2/9/18 - Per conan team, ranges are slow to resolve.
    # So, with libs like zlib, updates are very rare, so we now use static version


    #requires = (
    #    "OpenSSL/[>=1.0.2l]@conan/stable",
    #    "zlib/1.2.11@conan/stable"
    #)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires("msys2_installer/latest@bincrafters/stable")

    def source(self):
        source_url = "https://sourceforge.net/projects/mpg123/files/mpg123/{0}/mpg123-{0}.tar.bz2/download".format(self.version)
        tools.get(source_url)
        extracted_dir = self.name + "-" + self.version

        #Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        self._build_configure()

    def _build_configure(self):
        with tools.chdir(self.source_subfolder):
            #with tools.environment_append(env_vars):
            env_build = AutoToolsBuildEnvironment(self, win_bash=(self.settings.os == 'Windows'))
            env_build.fPIC = self.options.fPIC
            env_build.configure()
            env_build.make()
            #env_build.make(args=['install'])

    def package(self):
        self.copy(pattern="LICENSE", dst="license", src=self.source_subfolder)
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
