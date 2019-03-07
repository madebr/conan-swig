[![Download](https://api.bintray.com/packages/bincrafters/public-conan/swig_installer%3Abincrafters/images/download.svg) ](https://bintray.com/bincrafters/public-conan/swig_installer%3Abincrafters/_latestVersion)
[![Build Status Travis](https://travis-ci.com/bincrafters/conan-swig_installer.svg?branch=stable%2F3.0.12)](https://travis-ci.com/bincrafters/conan-swig_installer)
[![Build Status AppVeyor](https://ci.appveyor.com/api/projects/status/github/bincrafters/conan-swig_installer?branch=stable%2F3.0.12&svg=true)](https://ci.appveyor.com/project/bincrafters/conan-swig_installer)

## Conan package recipe for [*swig_installer*](http://www.swig.org)

SWIG is a software development tool that connects programs written
                     in C and C++ with a variety of high-level programming languages.

The packages generated with this **conanfile** can be found on [Bintray](https://bintray.com/bincrafters/public-conan/swig_installer%3Abincrafters).


## Issues

If you wish to report an issue or make a request for a package, please do so here:

[Issues Tracker](https://github.com/bincrafters/community/issues)


## For Users

### Basic setup

    $ conan install swig_installer/3.0.12@bincrafters/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    swig_installer/3.0.12@bincrafters/stable

    [generators]
    txt

Complete the installation of requirements for your project running:

    $ mkdir build && cd build && conan install ..

Note: It is recommended that you run conan install from a build directory and not the root of the project directory.  This is because conan generates *conanbuildinfo* files specific to a single build configuration which by default comes from an autodetected default profile located in ~/.conan/profiles/default .  If you pass different build configuration options to conan install, it will generate different *conanbuildinfo* files.  Thus, they should not be added to the root of the project, nor committed to git.


## Build and package

The following command both runs all the steps of the conan file, and publishes the package to the local system cache.  This includes downloading dependencies from "build_requires" and "requires" , and then running the build() method.

    $ conan create . bincrafters/stable




## Add Remote

    $ conan remote add bincrafters "https://api.bintray.com/conan/bincrafters/public-conan"


## Conan Recipe License

NOTE: The conan recipe license applies only to the files of this recipe, which can be used to build and package swig_installer.
It does *not* in any way apply or is related to the actual software being packaged.

[MIT](https://github.com/bincrafters/conan-swig/blob/stable/3.0.12/LICENSE.md)
