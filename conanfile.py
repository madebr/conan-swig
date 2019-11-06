from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import glob
import os
import shutil


class SwigConan(ConanFile):
    name = "swig_installer"
    version = "4.0.1"
    description = "SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages."
    topics = ("conan", "swig", "python", "java", "wrapper")
    url = "https://github.com/bincrafters/conan-swig_installer"
    homepage = "http://www.swig.org"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "GPL-3.0-or-later"
    exports = ["LICENSE.md"]
    exports_sources = "patches/*.patch"
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
            self.build_requires("msys2/20161025")
        if self.settings.os_build == "Windows":
            self.build_requires("winflexbison/2.5.18@bincrafters/stable")
        else:
            self.build_requires("bison_installer/3.3.2@bincrafters/stable")
        self.build_requires("pcre/8.41")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("cccl_installer/1.0@bincrafters/stable")

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
        sha256 = "2eaf6fb89d071d1be280bf995c63360b3729860c0da64948123b5d7e4cfb6cb7"
        foldername = "swig-rel-{}".format(self.version)

        tools.get(url, sha256=sha256)
        os.rename(foldername, self._source_subfolder)

    @contextmanager
    def _build_environment(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                yield
        else:
            yield

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure.ac"),
                              "AC_DEFINE_UNQUOTED(SWIG_LIB_WIN_UNIX",
                              "SWIG_LIB_WIN_UNIX=""\nAC_DEFINE_UNQUOTED(SWIG_LIB_WIN_UNIX")
        for patch in glob.glob(os.path.join("patches/*")):
            tools.patch(patch_file=patch, base_path=self._source_subfolder)

    def build(self):
        self._patch_sources()
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
            self.run('./autogen.sh', win_bash=tools.os_info.is_windows)
        env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        deps_libpaths = env_build.library_paths
        deps_libs = env_build.libs
        deps_defines = env_build.defines
        if self.settings.os_build == "Windows" and self.settings.compiler != "Visual Studio":
            env_build.link_flags.append("-static")

        libargs = list("-L\"{}\"".format(p) for p in deps_libpaths) + list("-l\"{}\"".format(l) for l in deps_libs)
        args = [
            "PCRE_LIBS={}".format(" ".join(libargs)),
            "PCRE_CPPFLAGS={}".format(" ".join("-D{}".format(define) for define in deps_defines)),
            "--host={}".format(tools.detected_architecture()),
        ]
        if self.settings.compiler == "Visual Studio":
            self.output.warn("Visual Studio compiler cannot create ccache-swig. Disabling ccache-swig.")
            args.append("--disable-ccache")
        with self._build_environment():
            env_build.configure(configure_dir=os.path.join(self.build_folder, self._source_subfolder), args=args)
            with tools.environment_append({"CONAN_CPU_COUNT": "1" if self.settings.compiler == "Visual Studio" else str(tools.cpu_count())}):
                env_build.make()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self.build_folder):
            env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            env_build.install()

            shutil.move(os.path.join(self.package_folder, "share", "swig", self.version),
                        os.path.join(self.package_folder, "bin", "Lib"))
            shutil.rmtree(os.path.join(self.package_folder, "share"))

            if self.settings.compiler != "Visual Studio":
                with tools.chdir(os.path.join(self.package_folder, "bin")):
                    ext = ".exe" if tools.os_info.is_windows else ""
                    self.run("strip swig{}".format(ext), win_bash=tools.os_info.is_windows)
                    self.run("strip ccache-swig{}".format(ext), win_bash=tools.os_info.is_windows)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        swig_lib_path = os.path.join(self.package_folder, "bin", "Lib")

        self.output.info('Setting SWIG_LIB environment variable: {}'.format(swig_lib_path))
        self.env_info.SWIG_LIB = swig_lib_path

        self.output.info('Setting SWIG_INSTALLER_ROOT to {}'.format(self.package_folder))
        self.env_info.SWIG_INSTALLER_ROOT = self.package_folder
