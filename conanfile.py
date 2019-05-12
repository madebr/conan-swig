# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os 
import shutil


class SwigConan(ConanFile):
    name = "swig_installer"
    version = "4.0.0"
    description = "SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages."

    topics = ("conan", "swig", "python", "java", "wrapper")
    url = "https://github.com/ss1978/conan-swig.git"
    homepage = "http://www.swig.org"
    author = "bincrafters <bincrafters@gmail.com>"
    license = "GPL-3.0"
    exports = ["LICENSE.md"]
    settings = "os_build", "arch_build", "compiler"
    _source_subfolder = "source_subfolder"

    @property
    def _url_filename_sha256_foldername(self):
        if self.settings.os_build == "Windows":
            return (
                "http://prdownloads.sourceforge.net/swig/swigwin-{}.zip".format(self.version),
                "{}win-{}.zip".format("swig", self.version),
                "1391aecad92e365b960eb1a1db3866ca1beee61b3395c182298edbf323d1695a",
                "{}win-{}".format("swig", self.version),
            )
        else:
            return (
                "https://github.com/swig/swig/archive/rel-{}.tar.gz".format(self.version),
                "{}-rel-{}.tar.gz".format("swig", self.version),
                "ab5cbf226ec50855aeca08193fbaafe92fe99b2454848b82f444ec96aa246b47",
                "{}-rel-{}".format("swig", self.version),
            )

    def build_requirements(self):
        if self.settings.os_build != "Windows":
            self.build_requires("pcre/8.41@bincrafters/stable")
            if tools.os_info.is_windows:
                pass
            else:
                self.build_requires("bison_installer/3.3.2@bincrafters/stable")

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

    def build(self):
        url, filename, sha256, foldername = self._url_filename_sha256_foldername
        tools.get(url, sha256=sha256)
        os.rename(foldername, self._source_subfolder)

        if self.settings.os_build == "Windows":
            pass
        else:
            env_build = AutoToolsBuildEnvironment(self)
            with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
                self.run('./autogen.sh')
            args = [
                "PCRE_LIBS={}".format(" ".join("-l{}".format(lib) for lib in self.deps_cpp_info["pcre"].libs)),
                "PCRE_CPPFLAGS={}".format(""),
                "--host={}".format(tools.detected_architecture()),
            ]
            env_build.configure(configure_dir=os.path.join(self.build_folder, self._source_subfolder), args=args)
            env_build.make()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.os_build == "Windows":
            self.copy("swig.exe", src=os.path.join(self.build_folder, self._source_subfolder), dst="bin")
            shutil.copytree(os.path.join(self.build_folder, self._source_subfolder, "Lib"), os.path.join(self.package_folder, "share", "swig", self.version))
        else:
            with tools.chdir(self.build_folder):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.install()
                with tools.chdir(os.path.join(self.package_folder, "bin")):
                    self.run("strip swig")
                    self.run("strip ccache-swig")

    def package_id(self):
        del self.info.settings.compiler
        if self.settings.os_build == "Windows":
            del self.info.settings.arch_build

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        swig_lib_path = os.path.join(self.package_folder, "share", "swig", self.version)
        self.output.info('Setting SWIG_LIB environment variable: {}'.format(swig_lib_path))
        self.env_info.SWIG_LIB = swig_lib_path

        self.output.info('Setting SWIG_INSTALLER_ROOT to {}'.format(self.package_folder))
        self.env_info.SWIG_INSTALLER_ROOT = self.package_folder
