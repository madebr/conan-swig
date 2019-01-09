#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os 

class SwigConan(ConanFile):
    name = "swig"
    version = "3.0.12"
    description = """SWIG is a software development tool that connects programs written
                     in C and C++ with a variety of high-level programming languages."""

    topics = ("conan", "swig", "python", "java", "wrapper")
    url = "https://github.com/ss1978/conan-swig.git"
    homepage = "https://www.swig.org"
    author = ""
    license = "https://github.com/swig/swig/blob/master/LICENSE"
    requires = "pcre/8.41@bincrafters/stable"
    exports = ["LICENSE.md"]
    settings = "os_build", "compiler", "arch_build"
    options = {
        "tests": [True, False]
    }

    default_options = {
        "tests": False
    }

    _download_url = "https://github.com/swig/swig/archive/rel-%s.tar.gz" % version
    _sha256 = "64971de92b8a1da0b9ffb4b51e9214bb936c4dbbc304367899cdb07280b94af6"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(self._download_url, sha256=self._sha256)
        extracted_dir = self.name + "-rel-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if not os.path.exists(self._source_subfolder):
            self.source()
        win_bash = True if self.settings.os_build=="Windows" else False
        build_folder = os.path.abspath(self._build_subfolder)
        with tools.chdir(os.path.abspath(self._source_subfolder)):
            args = ["--disable-dependency-tracking", "--without-alllang"]
            args.append('--prefix={}'.format(build_folder))
            if win_bash:
                self.run("pacman -S autoconf automake", win_bash=win_bash)
            self.run('./autogen.sh', win_bash=win_bash)
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])
            if not self.settings.os_build=="Windows":
                with tools.chdir(os.path.join(build_folder, "bin")):
                    self.run("strip swig")
                    self.run("strip ccache-swig")

    def package(self):
        self.build()
        
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="bin", src=os.path.join(self._build_subfolder, "bin"))
        self.copy("*", dst="share", src=os.path.join(self._build_subfolder, "share"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.env_info.SWIG_LIB=os.path.join(self.package_folder, "share", "swig", self.version )
