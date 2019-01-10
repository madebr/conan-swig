#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os 
import shutil

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
    #requires = "pcre/8.41@bincrafters/stable"
    exports = ["LICENSE.md"]
    settings = "os_build", "compiler", "arch_build"
    options = {
        "tests": [True, False]
    }

    default_options = {
        "tests": False
    }

    _pcre_download_url = "https://sourceforge.net/projects/pcre/files/pcre/8.42/pcre-8.42.tar.gz/download"
    _download_url = "https://github.com/swig/swig/archive/rel-%s.tar.gz" % version
    _win_download_url = "http://prdownloads.sourceforge.net/swig/swigwin-%s.zip" % version
    _sha256 = "64971de92b8a1da0b9ffb4b51e9214bb936c4dbbc304367899cdb07280b94af6"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        """
        On non-windows system, downloads the swig, and pcre source.
        On windows system, downloads the binary distribution for repackaging.
        """
        if self.settings.os_build=="Windows": 
            tools.get(self._win_download_url)
            os.rename("swigwin-%s"%self.version, self._source_subfolder)
        else:
            tools.get(self._download_url, sha256=self._sha256)
            extracted_dir = self.name + "-rel-" + self.version
            os.rename(extracted_dir, self._source_subfolder)
            tools.download(self._pcre_download_url, os.path.join(self._source_subfolder,"pcre-8.42.tar.gz"),overwrite=True)

    def build(self):
        """
        Builds the package structure.
        On non-windows system compiling swig with embedded pcre.
        On windows, simply copying the files to the appropriate structure.
        """
        build_folder = os.path.abspath(self._build_subfolder)
        if self.settings.os_build=="Windows": 
            if not os.path.exists(os.path.join(build_folder,"bin", "swig.exe")):
                os.makedirs(os.path.join(build_folder,"bin"))
                shutil.copyfile(os.path.join(self._source_subfolder,"swig.exe"), os.path.join(build_folder,"bin", "swig.exe"))
                os.makedirs(os.path.join(build_folder,"share","swig"))
                shutil.copytree(os.path.join(self._source_subfolder,"Lib"), os.path.join(build_folder,"share","swig",self.version))
        else:
            with tools.chdir(os.path.abspath(self._source_subfolder)):
                args = ["--disable-dependency-tracking", "--without-alllang"]
                args.append('--prefix={}'.format(build_folder))
                self.run('./autogen.sh')
                self.run('./Tools/pcre-build.sh')
                env_build = AutoToolsBuildEnvironment(self)
                env_build.configure(args=args)
                env_build.make()
                env_build.make(args=['install'])
                with tools.chdir(os.path.join(build_folder, "bin")):
                    self.run("strip swig")
                    self.run("strip ccache-swig")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="bin", src=os.path.join(self._build_subfolder, "bin"))
        self.copy("*", dst="share", src=os.path.join(self._build_subfolder, "share"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.env_info.SWIG_LIB=os.path.join(self.package_folder, "share", "swig", self.version )
