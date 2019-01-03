#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class Mpg123Conan(ConanFile):
    name = "mpg123"
    version = "1.25.6"
    description = "Fast MPEG Audio decoder library"
    topics = ("conan", "libmpg123", "audio", "mpeg", "mp3")
    url = "https://github.com/sixten-hilborn/conan-mpg123"
    homepage = "https://www.mpg123.de"
    author = "Sixten Hilborn <sixten.hilborn@gmail.com>"
    license = "LGPL-2.1"
    exports = ["LICENSE.md"]

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.compiler == 'Visual Studio':
            self.build_requires("yasm_installer/[>=1.3]@bincrafters/stable")

    def source(self):
        source_url = "https://sourceforge.net/projects/mpg123/files/mpg123/{0}/mpg123-{0}.tar.bz2".format(self.version)
        tools.get(source_url)
        extracted_dir = self.name + "-" + self.version

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self._build_vs()
        else:
            self._build_configure()

    def _build_vs(self):
        msbuild = MSBuild(self)
        # The VS project defines different configurations for Dll/static and "Generic"/x86-optimizations (SSE etc) 
        dll_suffix = "_Dll" if self.options.shared else ""
        # suffix "x86" uses more CPU specific optimizations, however it doesn't compile for arch==x86, only arch==x86_64
        optimization_suffix = "x86" if self.settings.arch == "x86_64" else "Generic"
        build_type = "{0}_{1}{2}".format(self.settings.build_type, optimization_suffix, dll_suffix)
        msbuild.build("{0}/ports/MSVC++/2015/win32/libmpg123/libmpg123.vcxproj".format(self._source_subfolder), build_type=build_type)

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.fPIC = self.options.fPIC
            env_build.configure()
            env_build.make()

    def package_id(self):
        # Can only build for 2015+ when using Visual Studio because of project file version,
        # however older VS can still link against binaries built with newer VS since it's a C library (stable ABI)
        if self.settings.compiler == "Visual Studio" and int(str(self.settings.compiler.version)) <= 14:
            self.info.settings.compiler.version = "VS2015"

    def package(self):
        self.copy(pattern="fmt123.h", dst="include", src=os.path.join(self._source_subfolder, "src", "libmpg123"))
        self.copy(pattern="mpg123.h*", dst="include", src=os.path.join(self._source_subfolder, "src", "libmpg123"))
        if self.settings.compiler == 'Visual Studio':
            self.copy("mpg123.h", dst="include", src=os.path.join(self._source_subfolder, "ports", "MSVC++"))
        self.copy(pattern="*mpg123.dll", dst="bin", keep_path=False)
        self.copy(pattern="*mpg123.lib", dst="lib", keep_path=False)
        self.copy(pattern="*mpg123.a", dst="lib", keep_path=False)
        self.copy(pattern="*mpg123.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy(pattern="*mpg123*.dylib", dst="lib", keep_path=False, symlinks=True)

    def package_info(self):
        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.libs = ['libmpg123']
        else:
            self.cpp_info.libs = ['mpg123']
