# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class SwigConan(ConanFile):
    name = "swig_installer"
    version = "4.0.0"
    description = "SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages."

    topics = ("conan", "swig", "python", "java", "wrapper", )
    url = "https://github.com/ss1978/conan-swig.git"
    homepage = "http://www.swig.org"
    author = "bincrafters <bincrafters@gmail.com>"
    license = "GPL-3.0"
    exports = ["LICENSE.md"]
    settings = "os_build", "arch_build", "compiler", "os", "arch"

    _source_subfolder = "source_subfolder"

    def configure(self):
        # Verify build configuration
        if str(self.settings.os_build) != str(self.settings.os):
            raise ConanInvalidConfiguration("settings.os_build must be equal to settings.os")
        if str(self.settings.arch_build) != str(self.settings.arch_build):
            raise ConanInvalidConfiguration("settings.arch_build must be equal to settings.arch_build")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.os
        del self.info.settings.arch
        self.info.include_build_settings()

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("msys2_installer/20161025@bincrafters/stable")
        if self.settings.os_build == "Windows":
            self.build_requires("winflexbison/2.5.18@bincrafters/stable")
        else:
            self.build_requires("bison_installer/3.3.2@bincrafters/stable")
        self.build_requires("pcre/8.41@bincrafters/stable")

    def system_requirements(self):
        if self.develop:
            if tools.os_info.with_yum:
                installer = tools.SystemPackageTool()
                packages = [
                    "autoconf",
                    "automake",
                ]
                for package in packages:
                    installer.install(package)

    def source(self):
        url = "https://github.com/swig/swig/archive/rel-{}.tar.gz".format(self.version)
        sha256 = "ab5cbf226ec50855aeca08193fbaafe92fe99b2454848b82f444ec96aa246b47"
        foldername = "swig-rel-{}".format(self.version)

        tools.get(url, sha256=sha256)
        os.rename(foldername, self._source_subfolder)

    def build(self):
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
            self.run('./autogen.sh', win_bash=tools.os_info.is_windows)
        env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if tools.os_info.is_windows:
            env_build.link_flags.append("-static")
        args = [
            "PCRE_LIBS={}".format(" ".join("-l{}".format(lib) for lib in self.deps_cpp_info["pcre"].libs)),
            "PCRE_CPPFLAGS={}".format(" ".join("-D{}".format(define) for define in self.deps_cpp_info["pcre"].defines)),
            "--host={}".format(tools.detected_architecture()),
            "--enable-cpp11-testing",
        ]
        env_build.configure(configure_dir=os.path.join(self.build_folder, self._source_subfolder), args=args)
        env_build.make()

    def package(self):
        with tools.chdir(self.build_folder):
            env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            env_build.install()
            with tools.chdir(os.path.join(self.package_folder, "bin")):
                ext = ".exe" if tools.os_info.is_windows else ""
                self.run("strip swig{}".format(ext), win_bash=tools.os_info.is_windows)
                self.run("strip ccache-swig{}".format(ext), win_bash=tools.os_info.is_windows)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        swig_lib_path = os.path.join(self.package_folder, "share", "swig", self.version)
        self.output.info('Setting SWIG_LIB environment variable: {}'.format(swig_lib_path))
        self.env_info.SWIG_LIB = swig_lib_path

        self.output.info('Setting SWIG_INSTALLER_ROOT to {}'.format(self.package_folder))
        self.env_info.SWIG_INSTALLER_ROOT = self.package_folder
